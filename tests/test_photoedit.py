import hashlib
import os
import sys
import threading
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from memoria.engine import photoedit as pe  # noqa: E402
from memoria.engine.progress import Cancelled, Progress  # noqa: E402

_ORIENT, _EXIF_IFD, _GPS_IFD, _DTO = 0x0112, 0x8769, 0x8825, 0x9003


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _arr(img) -> np.ndarray:
    return np.asarray(img.convert("RGB")).astype(np.int16)


def _photo_like(w: int, h: int, seed: int = 1) -> Image.Image:
    """Smooth colour fields + fine texture, so JPEG behaves roughly like on a real photo."""
    rng = np.random.default_rng(seed)
    low = Image.fromarray(rng.integers(0, 255, (9, 12, 3), dtype=np.uint8)).resize((w, h), Image.Resampling.BICUBIC)
    mid = Image.fromarray(rng.integers(0, 255, (h // 40, w // 40, 3), dtype=np.uint8)).resize(
        (w, h), Image.Resampling.BICUBIC)
    a = 0.7 * np.asarray(low, np.float32) + 0.3 * np.asarray(mid, np.float32)
    a += rng.normal(0, 6, (h, w, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


@pytest.fixture
def exif_jpeg(tmp_path) -> Path:
    """A 300×200 stored JPEG with Orientation 6 (displayed 200×300), GPS and DateTimeOriginal."""
    img = Image.new("RGB", (300, 200), (30, 60, 200))
    img.paste((250, 20, 20), (0, 0, 60, 40))  # red block at stored top-left
    exif = Image.Exif()
    exif[_ORIENT] = 6
    exif[0x010F] = "Canon"
    exif[0x0110] = "Canon EOS 80D"
    exif[_EXIF_IFD] = {_DTO: "2019:07:14 10:20:30"}
    exif[_GPS_IFD] = {1: "N", 2: (48.0, 51.0, 30.0), 3: "E", 4: (2.0, 17.0, 40.0)}
    p = tmp_path / "src" / "IMG_0001.jpg"
    p.parent.mkdir()
    img.save(p, "JPEG", quality=95, exif=exif.tobytes())
    os.utime(p, (1_500_000_000, 1_500_000_000))
    return p


def test_identity_copy_and_constants():
    e = pe.PhotoEdit()
    assert e.is_identity()
    assert not e.copy(rotate=90).is_identity()
    assert not e.copy(format="webp").is_identity()
    assert not e.copy(strip_gps=True).is_identity()
    assert e.copy(crop=(0, 0, 1, 1)).is_identity()
    assert e.copy(rotate=90) is not e and e.rotate == 0
    assert set(pe.FILTERS) >= {"none", "bw", "sepia", "vivid", "warm", "cool", "fade"}
    assert pe.ASPECTS["4:5"] == 0.8 and pe.FORMATS["same"]


def test_rotate_and_flip_pixel_mapping():
    a = np.array([[[255, 0, 0], [0, 255, 0], [0, 0, 255]],
                  [[255, 255, 0], [0, 255, 255], [255, 0, 255]]], dtype=np.uint8)  # 3×2, all distinct
    img = Image.fromarray(a)
    cases = [
        (pe.PhotoEdit(rotate=90), np.rot90(a, -1)),
        (pe.PhotoEdit(rotate=180), np.rot90(a, 2)),
        (pe.PhotoEdit(rotate=270), np.rot90(a, 1)),
        (pe.PhotoEdit(flip_h=True), a[:, ::-1]),
        (pe.PhotoEdit(flip_v=True), a[::-1]),
        (pe.PhotoEdit(rotate=90, flip_h=True), np.rot90(a, -1)[:, ::-1]),
    ]
    for edit, want in cases:
        out = pe.apply(img, edit)
        assert np.array_equal(np.asarray(out), want), edit
        assert pe.transform(img, edit).size == out.size


def test_crop_is_exact_pixel_box():
    yy, xx = np.mgrid[0:50, 0:100]
    a = np.dstack([xx * 2, yy * 5, np.zeros_like(xx)]).astype(np.uint8)
    out = pe.apply(Image.fromarray(a), pe.PhotoEdit(crop=(0.1, 0.2, 0.5, 0.8)))
    assert out.size == (40, 30)
    assert np.array_equal(np.asarray(out), a[10:40, 10:50])
    assert pe.crop_box((100, 50), (0.1, 0.2, 0.5, 0.8)) == (10, 10, 50, 40)


def test_crop_for_aspect():
    assert pe.crop_for_aspect(400, 300, 1.0) == pytest.approx((0.125, 0, 0.875, 1))
    l, t, r, b = pe.crop_for_aspect(400, 300, 16 / 9)
    assert (r - l) * 400 / ((b - t) * 300) == pytest.approx(16 / 9) and r - l == pytest.approx(1)
    l, t, r, b = pe.crop_for_aspect(400, 300, 1.0, base=(0.5, 0.0, 1.0, 1.0))
    assert (l, r) == pytest.approx((0.5, 1.0)) and (b - t) * 300 == pytest.approx(200)
    assert pe.crop_for_aspect(400, 300, "original") == pytest.approx((0, 0, 1, 1))
    assert pe.crop_for_aspect(400, 300, None) == (0, 0, 1, 1)


@pytest.mark.parametrize("angle", [7.5, -12.0, 0.6])
def test_straighten_auto_crop_has_no_empty_corners(angle):
    img = Image.new("RGB", (600, 400), (255, 255, 255))
    out = pe.apply(img, pe.PhotoEdit(straighten=angle))
    a = _arr(out)
    assert out.width < 600 and out.height < 400 and out.width > 300
    assert a.min() > 200  # no black fill anywhere, corners included
    # rotation direction: a marker on the right edge moves down for clockwise straighten
    marked = img.copy()
    marked.paste((0, 0, 0), (560, 180, 600, 220))
    t = pe.transform(marked, pe.PhotoEdit(straighten=10))
    ys, xs = np.nonzero(_arr(t).sum(axis=2) < 100)
    assert ys.size and ys.mean() > t.height / 2 + 10


def test_adjustments_move_in_the_right_direction():
    img = _photo_like(240, 160)
    base = _arr(img)

    def sat(a):
        return (a.max(axis=2) - a.min(axis=2)).mean()

    assert _arr(pe.apply(img, pe.PhotoEdit(brightness=50))).mean() > base.mean() + 10
    assert _arr(pe.apply(img, pe.PhotoEdit(brightness=-50))).mean() < base.mean() - 10
    assert _arr(pe.apply(img, pe.PhotoEdit(contrast=60))).std() > base.std() * 1.2
    assert _arr(pe.apply(img, pe.PhotoEdit(contrast=-60))).std() < base.std() * 0.8
    assert sat(_arr(pe.apply(img, pe.PhotoEdit(saturation=60)))) > sat(base) * 1.2
    gray = _arr(pe.apply(img, pe.PhotoEdit(saturation=-100)))
    assert sat(gray) <= 1
    warm = _arr(pe.apply(img, pe.PhotoEdit(warmth=60)))
    cool = _arr(pe.apply(img, pe.PhotoEdit(warmth=-60)))
    rb = lambda a: (a[..., 0] - a[..., 2]).mean()  # noqa: E731
    assert rb(warm) > rb(base) + 10 > rb(cool) + 20
    dull = Image.fromarray((np.asarray(img) * 0.5 + 60).astype(np.uint8))
    auto = _arr(pe.apply(dull, pe.PhotoEdit(auto=True)))
    assert auto.max() - auto.min() > _arr(dull).max() - _arr(dull).min() + 50
    sharp = _arr(pe.apply(img, pe.PhotoEdit(sharpness=100)))
    lap = lambda a: np.abs(np.diff(a.astype(np.float32), axis=1)).mean()  # noqa: E731
    assert lap(sharp) > lap(base)


def test_filters():
    img = _photo_like(120, 80)
    bw = _arr(pe.apply(img, pe.PhotoEdit(filter="bw")))
    assert (bw[..., 0] == bw[..., 1]).all() and (bw[..., 1] == bw[..., 2]).all()
    sepia = _arr(pe.apply(img, pe.PhotoEdit(filter="sepia")))
    assert (sepia[..., 0] >= sepia[..., 2]).all()
    for name in pe.FILTERS:
        out = pe.apply(img, pe.PhotoEdit(filter=name))
        assert out.size == img.size and out.mode == "RGB"
    assert np.array_equal(_arr(pe.apply(img, pe.PhotoEdit(filter="none"))), _arr(img))
    with pytest.raises(ValueError):
        pe.apply(img, pe.PhotoEdit(filter="nope"))


def test_resize_never_upscales_and_keeps_aspect():
    img = Image.new("RGB", (200, 100), "gray")
    assert pe.apply(img, pe.PhotoEdit(resize_long=50)).size == (50, 25)
    assert pe.apply(img, pe.PhotoEdit(resize_long=1000)).size == (200, 100)
    assert pe.apply(img.rotate(90, expand=True), pe.PhotoEdit(resize_long=80)).size == (40, 80)


def test_save_keeps_exif_date_resets_orientation_and_strips_gps(exif_jpeg, tmp_path):
    before = _sha(exif_jpeg)
    out1 = pe.save(exif_jpeg, pe.PhotoEdit())
    out2 = pe.save(exif_jpeg, pe.PhotoEdit(strip_gps=True))
    assert out1 == exif_jpeg.parent / "IMG_0001 (edited).jpg"
    assert out2 == exif_jpeg.parent / "IMG_0001 (edited) (2).jpg"
    assert _sha(exif_jpeg) == before
    assert sorted(p.name for p in exif_jpeg.parent.iterdir()) == [
        "IMG_0001 (edited) (2).jpg", "IMG_0001 (edited).jpg", "IMG_0001.jpg"]
    for out, has_gps in ((out1, True), (out2, False)):
        with Image.open(out) as im:
            assert im.size == (200, 300)  # stored upright
            ex = im.getexif()
            assert ex.get(_ORIENT) == 1
            assert ex.get_ifd(_EXIF_IFD).get(_DTO) == "2019:07:14 10:20:30"
            assert ex.get(0x0110) == "Canon EOS 80D"
            assert bool(ex.get_ifd(_GPS_IFD)) is has_gps
            a = _arr(im)
        # the red block (stored top-left) is at the top-right after the 90° clockwise orientation
        assert a[5, 195, 0] > 200 and a[5, 195, 2] < 80 and a[295, 5, 2] > 150
        assert out.stat().st_mtime == pytest.approx(exif_jpeg.stat().st_mtime, abs=0.01)
    assert not [p for p in exif_jpeg.parent.iterdir() if p.name.startswith(".memoria-work")]


def test_format_and_quality(exif_jpeg, tmp_path):
    src = tmp_path / "big.jpg"
    _photo_like(800, 600).save(src, quality=95)
    before = _sha(src)
    hi = pe.save(src, pe.PhotoEdit(quality=95), tmp_path / "o")
    lo = pe.save(src, pe.PhotoEdit(quality=40), tmp_path / "o")
    webp = pe.save(src, pe.PhotoEdit(format="webp", quality=60), tmp_path / "o")
    png = pe.save(src, pe.PhotoEdit(format="png", resize_long=400), tmp_path / "o", suffix=" (small)")
    assert lo.stat().st_size < hi.stat().st_size
    assert webp.suffix == ".webp" and png.name == "big (small).png"
    with Image.open(webp) as im:
        assert im.format == "WEBP" and im.size == (800, 600)
    with Image.open(png) as im:
        assert im.format == "PNG" and im.size == (400, 300)
    assert pe.output_path(src, fmt="webp") == tmp_path / "big (edited).webp"
    assert pe.output_path(src, tmp_path / "o") == tmp_path / "o" / "big (edited) (3).jpg"
    assert pe.output_path(tmp_path / "x.heic") == tmp_path / "x (edited).jpg"
    assert _sha(src) == before


def test_png_alpha_is_kept_for_png_and_flattened_for_jpeg(tmp_path):
    src = tmp_path / "logo.png"
    img = Image.new("RGBA", (40, 20), (255, 0, 0, 255))
    img.paste((0, 0, 255, 0), (0, 0, 20, 20))  # left half fully transparent
    img.save(src)
    before = _sha(src)
    out = pe.save(src, pe.PhotoEdit(rotate=180))
    with Image.open(out) as im:
        assert im.format == "PNG" and im.mode == "RGBA" and im.size == (40, 20)
        a = np.asarray(im)
        assert a[10, 35, 3] == 0 and a[10, 5, 3] == 255  # transparency rotated with the pixels
    jpg = pe.save(src, pe.PhotoEdit(format="jpeg"))
    with Image.open(jpg) as im:
        assert im.mode == "RGB" and np.asarray(im)[10, 5].min() > 230  # flattened on white
    assert _sha(src) == before


def test_heic_saved_as_jpeg(tmp_path):
    pillow_heif = pytest.importorskip("pillow_heif")
    pillow_heif.register_heif_opener()
    src = tmp_path / "phone.heic"
    try:
        Image.new("RGB", (64, 48), (200, 120, 40)).save(src, format="HEIF", quality=80)
    except Exception as e:  # pragma: no cover - encoder not bundled
        pytest.skip(f"HEIF encoder unavailable: {e}")
    before = _sha(src)
    out = pe.save(src, pe.PhotoEdit(brightness=10))
    assert out.name == "phone (edited).jpg"
    with Image.open(out) as im:
        assert im.format == "JPEG" and im.size == (64, 48)
    assert pe.load(src).size == (64, 48) and pe.load(src, 32).size == (32, 24)
    assert _sha(src) == before


def test_split_grid_tiles_reassemble_exactly(tmp_path):
    src = tmp_path / "pano.png"
    _photo_like(301, 199).save(src)
    before = _sha(src)
    parts = pe.split_grid(src, 2, 3, tmp_path / "out")
    assert [p.name for p in parts] == [f"pano (part {i} of 6).png" for i in range(1, 7)]
    tiles = [Image.open(p).convert("RGB") for p in parts]
    rows = [np.hstack([np.asarray(t) for t in tiles[r * 3:r * 3 + 3]]) for r in range(2)]
    assert np.array_equal(np.vstack(rows), np.asarray(Image.open(src).convert("RGB")))
    for t in tiles:
        t.close()
    assert _sha(src) == before

    jsrc = tmp_path / "pic.jpg"
    _photo_like(200, 100).save(jsrc)
    jparts = pe.split_grid(jsrc, 1, 2, edit=pe.PhotoEdit(rotate=90))
    assert [p.name for p in jparts] == ["pic (part 1 of 2).jpg", "pic (part 2 of 2).jpg"]
    assert [Image.open(p).size for p in jparts] == [(50, 200), (50, 200)]


def test_join_sizes(tmp_path):
    srcs = []
    for i, size in enumerate([(200, 100), (100, 100), (300, 150)]):
        p = tmp_path / f"p{i}.jpg"
        Image.new("RGB", size, (50 * i, 100, 150)).save(p)
        srcs.append(p)
    h = pe.join(srcs, "horizontal")
    assert h.name == "p0 (joined).jpg"
    assert Image.open(h).size == (500, 100)
    v = pe.join(srcs, "vertical", tmp_path / "o", spacing=10, background="#000000")
    assert Image.open(v).size == (100, 50 + 100 + 50 + 20)
    a = _arr(Image.open(v))
    assert a[55, 50].max() < 30  # spacing is filled with the background colour
    g = pe.join(srcs + srcs[:2], "grid", tmp_path / "o")  # 5 photos → 3 × 2 grid of 2:1 cells
    assert Image.open(g).size == (3 * 100, 2 * 50)
    h2 = pe.join(srcs, "horizontal")
    assert h2.name == "p0 (joined) (2).jpg"


def test_join_never_exceeds_max_side(tmp_path, monkeypatch):
    monkeypatch.setattr(pe, "MAX_JOIN_SIDE", 300)
    srcs = []
    for i in range(3):
        p = tmp_path / f"q{i}.png"
        Image.new("RGB", (200, 100), "white").save(p)
        srcs.append(p)
    out = pe.join(srcs, "horizontal")
    assert Image.open(out).size == (300, 50)


def test_estimate_bytes_is_close_for_jpeg(tmp_path):
    src = tmp_path / "photo.jpg"
    _photo_like(2400, 1600, seed=3).save(src, quality=95)
    full = pe.load(src)
    for edit in (pe.PhotoEdit(quality=85), pe.PhotoEdit(quality=70, rotate=90, crop=(0.1, 0.1, 0.9, 0.9)),
                 pe.PhotoEdit(resize_long=1200), pe.PhotoEdit(format="webp", quality=80)):
        real = pe.save(src, edit, tmp_path / "o").stat().st_size
        est = pe.estimate_bytes(full, edit, full.size, src=src)
        assert 0.6 * real <= est <= 1.4 * real, (edit, est, real)
    # From a preview (what the editor has on screen) on a photo without pixel-level noise.
    smooth = tmp_path / "smooth.jpg"
    Image.fromarray(np.asarray(_photo_like(2400, 1600, seed=4))).filter(ImageFilter.GaussianBlur(1.2)).save(
        smooth, quality=95)
    preview = pe.load(smooth, 1000)
    for edit in (pe.PhotoEdit(quality=85), pe.PhotoEdit(quality=60, saturation=30)):
        real = pe.save(smooth, edit, tmp_path / "o").stat().st_size
        est = pe.estimate_bytes(preview, edit, (2400, 1600))
        assert 0.6 * real <= est <= 1.4 * real, (edit, est, real)


def test_save_many_reports_failures(tmp_path):
    good = []
    for i in range(2):
        p = tmp_path / f"g{i}.jpg"
        Image.new("RGB", (60 + i * 20, 40), "orange").save(p)
        good.append(p)
    bad = tmp_path / "broken.jpg"
    bad.write_bytes(b"not a jpeg at all")
    seen = []
    res = pe.save_many([good[0], bad, good[1]], pe.PhotoEdit(crop=(0, 0, 0.5, 1)), tmp_path / "o",
                       progress=Progress(lambda d, t, m: seen.append((d, t))))
    assert isinstance(res, list) and len(res) == 2
    assert [Image.open(p).size for p in res] == [(30, 40), (40, 40)]  # crop applied per photo
    assert [f[0] for f in res.failures] == [bad] and pe.save_many.last_failures == res.failures
    assert res.sources == [good[0], good[1]]
    assert seen[-1][0] == seen[-1][1] and all(t for _, t in seen)
    with pytest.raises(pe.PhotoEditError):
        pe.save_many([bad, tmp_path / "missing.jpg"], pe.PhotoEdit(), tmp_path / "o2")
    assert not list((tmp_path / "o2").iterdir())


def test_cancel_leaves_nothing(tmp_path):
    src = tmp_path / "c.jpg"
    _photo_like(400, 300).save(src)
    before = _sha(src)
    cancel = threading.Event()
    out = tmp_path / "out"
    with pytest.raises(Cancelled):
        pe.save(src, pe.PhotoEdit(rotate=90), out, progress=Progress(lambda d, t, m: cancel.set(), cancel))
    with pytest.raises(Cancelled):
        pe.split_grid(src, 2, 2, out, progress=Progress(lambda d, t, m: cancel.set(), cancel))
    assert list(out.iterdir()) == []
    assert _sha(src) == before
