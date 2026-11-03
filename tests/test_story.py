import sys
import threading
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from memoria.engine import ffmpeg  # noqa: E402
from memoria.engine import story as st  # noqa: E402
from memoria.engine.progress import Cancelled, Progress  # noqa: E402


def _photo(path: Path, w: int, h: int, seed: int) -> Path:
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rng = np.random.default_rng(seed)
    a = np.stack([
        xx / w * 255,
        yy / h * 255,
        127 + 100 * np.sin(xx / 37.0 + seed) * np.cos(yy / 53.0),
    ], -1)
    a += rng.normal(0, 4, a.shape)
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(path, quality=90)
    return path


@pytest.fixture(scope="module")
def photos(tmp_path_factory):
    d = tmp_path_factory.mktemp("photos")
    sizes = [(1800, 1200), (1000, 1500), (1200, 1200), (1600, 900), (900, 1600)]
    return [_photo(d / f"p{i}.jpg", w, h, i) for i, (w, h) in enumerate(sizes)]


@pytest.mark.parametrize("size", [st.STORY, st.POST, st.SQUARE])
def test_render_sizes_exact(photos, size):
    img = st.render_story(photos[:1], "single", st.StyleOptions(), size)
    assert img.size == size and img.mode == "RGB"


@pytest.mark.parametrize("template", list(st.TEMPLATES))
@pytest.mark.parametrize("background", ["blur", "white", "#336699"])
def test_every_template_renders(photos, template, background):
    style = st.StyleOptions(background=background, caption="Summer at the lake, 2024",
                            fit="fill" if background == "white" else "fit")
    n = st.template_slots(template)
    img = st.render_story(photos[:n], template, style, st.STORY)
    assert img.size == st.STORY
    a = np.asarray(img)
    assert a.std() > 10  # actually drew photos, not a flat colour


def test_template_slots_and_partial_group(photos):
    assert [st.template_slots(t) for t in ("single", "polaroid", "duo", "trio", "grid4", "before_after")] \
        == [1, 1, 2, 3, 4, 2]
    with pytest.raises(ValueError):
        st.template_slots("nope")
    assert st.render_story(photos[:3], "grid4", None, st.POST).size == st.POST


def test_exif_rotated_photo_renders_upright(tmp_path):
    upright = np.zeros((600, 400, 3), np.uint8)
    upright[:300] = (230, 30, 30)    # top half red
    upright[300:] = (30, 30, 230)    # bottom half blue
    stored = Image.fromarray(upright).rotate(90, expand=True)  # landscape on disk
    assert stored.size == (600, 400)
    exif = Image.Exif()
    exif[0x0112] = 6
    path = tmp_path / "rotated.jpg"
    stored.save(path, quality=95, exif=exif.tobytes())

    img = st.render_story([path], "single", st.StyleOptions(background="black"), st.STORY)
    a = np.asarray(img).astype(int)
    ys, xs = np.nonzero(a.max(axis=2) > 60)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    assert (y1 - y0) > 1.3 * (x1 - x0)  # portrait card
    cx = (x0 + x1) // 2
    top, bottom = a[y0 + 20, cx], a[y1 - 20, cx]
    assert top[0] > 150 and top[2] < 100
    assert bottom[2] > 150 and bottom[0] < 100


def test_heic_photo_renders(tmp_path):
    pillow_heif = pytest.importorskip("pillow_heif")
    path = tmp_path / "p.heic"
    try:
        pillow_heif.register_heif_opener()
        Image.new("RGB", (640, 480), (200, 120, 40)).save(path, format="HEIF", quality=80)
    except Exception as e:  # pragma: no cover - encoder not bundled
        pytest.skip(f"HEIF encoder unavailable: {e}")
    img = st.render_story([path], "single", st.StyleOptions(background="black"), st.POST)
    assert img.size == st.POST and np.asarray(img).max() > 100


def test_panorama_split_is_seamless(tmp_path):
    pano = _photo(tmp_path / "pano.jpg", 4000, 1000, 7)
    slides = st.render_carousel([pano], st.StyleOptions(), st.POST, panorama=True)
    assert len(slides) == round((4000 / 1000) / 0.8) == 5
    assert all(s.size == st.POST for s in slides)
    arrs = [np.asarray(s).astype(np.float32) for s in slides]
    interior = np.mean([np.abs(a[:, 1:] - a[:, :-1]).mean() for a in arrs])
    for left, right in zip(arrs, arrs[1:]):
        seam = np.abs(right[:, 0] - left[:, -1]).mean()
        assert seam <= max(2.0, 2.0 * interior), (seam, interior)

    narrow = _photo(tmp_path / "narrow.jpg", 1200, 1000, 8)
    assert len(st.render_carousel([narrow], None, st.POST, panorama=True)) == 2
    assert len(st.render_carousel(list(tmp_path.glob("*.jpg")), None, st.POST, panorama=True)) == 2


def test_export_stories_and_carousel_unique_names(photos, tmp_path):
    out = st.export_stories(photos, "duo", None, tmp_path)
    assert [p.name for p in out] == ["story-001.jpg", "story-002.jpg", "story-003.jpg"]
    again = st.export_stories(photos[:2], "duo", None, tmp_path)
    assert [p.name for p in again] == ["story-001 (2).jpg"]
    with Image.open(out[0]) as im:
        assert im.size == st.STORY and im.format == "JPEG"

    car = st.export_carousel(photos[:3], st.StyleOptions(background="white"), tmp_path)
    assert [p.name for p in car] == ["carousel-01.jpg", "carousel-02.jpg", "carousel-03.jpg"]
    with Image.open(car[1]) as im:
        assert im.size == st.POST
    assert not [p for p in tmp_path.iterdir() if p.name.startswith(".")]


def test_export_cancel_leaves_nothing(photos, tmp_path):
    cancel = threading.Event()
    progress = Progress(lambda d, t, m: cancel.set(), cancel)
    with pytest.raises(Cancelled):
        st.export_carousel(photos, None, tmp_path, progress=progress)
    assert list(tmp_path.iterdir()) == []


def test_story_video_duration_and_resolution(photos, tmp_path):
    n, spp, tr = 3, 1.5, 0.5
    out = st.make_story_video(photos[:n], tmp_path, seconds_per_photo=spp, transition=tr)
    assert out.name == "story-video.mp4"
    info = ffmpeg.probe(out)
    assert (info.width, info.height) == st.STORY
    assert abs(info.duration - (n * spp - (n - 1) * tr)) <= 0.2
    assert [p.name for p in tmp_path.iterdir()] == ["story-video.mp4"]


def test_story_video_with_music_and_unique_name(photos, tmp_path):
    music = tmp_path / "music.m4a"
    proc = ffmpeg.run_ffmpeg(["-y", "-f", "lavfi", "-i", "sine=frequency=330", "-t", "10",
                              "-c:a", "aac", str(music)], timeout=60)
    assert proc.returncode == 0
    (tmp_path / "story-video.mp4").write_bytes(b"existing")
    out = st.make_story_video(photos[:2], tmp_path, seconds_per_photo=1.2, transition=0.4,
                              ken_burns=False, size=st.SQUARE, music=music)
    assert out.name == "story-video (2).mp4"
    assert (tmp_path / "story-video.mp4").read_bytes() == b"existing"
    info = ffmpeg.probe(out)
    assert info.has_audio and (info.width, info.height) == st.SQUARE
    assert abs(info.duration - 2.0) <= 0.2


def test_story_video_cancel_cleans_up(photos, tmp_path):
    cancel = threading.Event()
    calls = []

    def cb(d, t, m):
        calls.append(d)
        if d >= 5:
            cancel.set()

    with pytest.raises(Cancelled):
        st.make_story_video(photos[:3], tmp_path, progress=Progress(cb, cancel, interval=0))
    assert list(tmp_path.iterdir()) == []
