"""Generate a deterministic test photo library with known ground truth.

Usage:
    python tools/make_test_library.py [DEST] [--small] [--no-video]

The library imitates a messy real collection: camera folders, phone backups, WhatsApp copies,
downloads, bursts, blurry shots, screenshots, junk files, a corrupt photo, rotated photos,
HEIC, and videos (including a WhatsApp-compressed copy and a trimmed copy that the similar-videos
tool must find). ``expected.json`` in the library root records what each tool should find.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from PIL.TiffImagePlugin import IFDRational

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DEST = ROOT / "test-library"
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

CAMERAS = [("Canon", "Canon EOS 200D"), ("Google", "Pixel 7"), ("Apple", "iPhone 13")]
PLACES = {"Goa": (15.4909, 73.8278), "Ladakh": (34.1526, 77.5771), "Delhi": (28.6139, 77.2090)}

EVENTS = [
    # (date, name, count, camera index, place, folder)
    ("2019-12-25 18:00:00", "Christmas", 6, 0, "Delhi", "DCIM\\100CANON"),
    ("2021-03-14 10:15:00", "Goa trip", 10, 1, "Goa", "Camera Roll\\2021"),
    ("2022-08-01 19:30:00", "Birthday", 6, 2, None, "iPhone Import"),
    ("2023-06-10 08:45:00", "Ladakh", 12, 0, "Ladakh", "DCIM\\101CANON"),
    ("2024-02-10 16:20:00", "Wedding", 8, 1, "Delhi", "Camera Roll\\2024"),
    ("2025-10-20 20:00:00", "Diwali", 6, 2, "Delhi", "iPhone Import"),
]

PALETTES = [
    ((70, 130, 200), (250, 200, 150), (60, 90, 60)),
    ((20, 40, 90), (230, 120, 80), (40, 40, 50)),
    ((120, 180, 230), (220, 235, 245), (150, 120, 80)),
    ((90, 60, 130), (250, 170, 110), (30, 70, 40)),
    ((160, 200, 220), (255, 250, 230), (200, 180, 140)),
    ((30, 30, 60), (90, 80, 140), (20, 20, 25)),
]


# --------------------------------------------------------------------------------------
# Procedural "photos"
# --------------------------------------------------------------------------------------
def scene(seed: int, w: int = 1600, h: int = 1200, shift: tuple[int, int] = (0, 0)) -> Image.Image:
    """A landscape-like picture with sky, sun, mountain ridges, trees and fine texture."""
    rng = np.random.default_rng(seed)
    pr = random.Random(seed)
    sky, horizon, ground = PALETTES[seed % len(PALETTES)]
    pad = 40
    W, H = w + 2 * pad, h + 2 * pad
    y = np.linspace(0, 1, H)[:, None, None]
    img = (np.array(sky) * (1 - y) + np.array(horizon) * y) * np.ones((1, W, 1))
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    sx, sy, sr = pr.randint(pad, W - pad), pr.randint(H // 10, H // 3), pr.randint(H // 20, H // 9)
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 240, 200))
    for layer in range(3):
        base = H * (0.45 + 0.12 * layer)
        pts, x = [(0, H)], 0
        yv = base + pr.uniform(-60, 60)
        while x <= W:
            pts.append((x, yv))
            x += pr.randint(25, 90)
            yv = min(H - 10, max(H * 0.25, yv + pr.uniform(-70, 70)))
        pts.append((W, H))
        shade = tuple(int(c * (0.55 + 0.2 * layer)) for c in ground)
        d.polygon(pts, fill=shade)
    for _ in range(pr.randint(10, 30)):
        tx, ty = pr.randint(0, W), pr.randint(int(H * 0.6), H)
        th = pr.randint(30, 140)
        d.rectangle([tx - 3, ty - th // 3, tx + 3, ty], fill=(60, 40, 30))
        d.polygon([(tx - th // 4, ty - th // 3), (tx + th // 4, ty - th // 3), (tx, ty - th)],
                  fill=(20 + pr.randint(0, 40), 80 + pr.randint(0, 60), 30))
    for _ in range(pr.randint(3, 8)):
        bx, by = pr.randint(0, W), pr.randint(int(H * 0.5), H)
        bw, bh = pr.randint(40, 160), pr.randint(40, 120)
        col = tuple(pr.randint(80, 240) for _ in range(3))
        d.rectangle([bx, by - bh, bx + bw, by], fill=col, outline=(30, 30, 30), width=3)
        for wx in range(bx + 8, bx + bw - 8, 20):
            d.rectangle([wx, by - bh + 10, wx + 8, by - bh + 22], fill=(250, 240, 180))
    arr = np.asarray(im, dtype=np.float32)
    arr += rng.normal(0, 4, arr.shape)
    ox, oy = pad + shift[0], pad + shift[1]
    arr = arr[oy:oy + h, ox:ox + w]
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def screenshot(seed: int, w: int = 1080, h: int = 2340) -> Image.Image:
    pr = random.Random(seed)
    im = Image.new("RGB", (w, h), (245, 246, 250))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, 140], fill=(40, 90, 200))
    try:
        font = ImageFont.truetype("segoeui.ttf", 44)
    except OSError:
        font = ImageFont.load_default()
    d.text((40, 45), f"Messages {seed}", fill="white", font=font)
    y = 200
    while y < h - 200:
        mine = pr.random() < 0.5
        bw, bh = pr.randint(300, 800), pr.randint(90, 220)
        x0 = w - bw - 40 if mine else 40
        d.rounded_rectangle([x0, y, x0 + bw, y + bh], 30, fill=(0, 132, 255) if mine else (225, 228, 235))
        d.text((x0 + 30, y + 25), "Lorem ipsum " * pr.randint(1, 3), fill="white" if mine else "black", font=font)
        y += bh + 40
    return im


def exif_bytes(dt: datetime, cam: int | None, place: str | None, orientation: int = 1) -> bytes:
    ex = Image.Exif()
    if cam is not None:
        make, model = CAMERAS[cam]
        ex[0x010F], ex[0x0110] = make, model
    ex[0x0132] = dt.strftime("%Y:%m:%d %H:%M:%S")
    if orientation != 1:
        ex[0x0112] = orientation
    sub = ex.get_ifd(0x8769)
    sub[0x9003] = dt.strftime("%Y:%m:%d %H:%M:%S")
    sub[0x9004] = dt.strftime("%Y:%m:%d %H:%M:%S")
    if place:
        lat, lon = PLACES[place]
        gps = ex.get_ifd(0x8825)

        def dms(v):
            v = abs(v)
            d_ = int(v)
            m = int((v - d_) * 60)
            s = round(((v - d_) * 60 - m) * 60, 2)
            return (IFDRational(d_, 1), IFDRational(m, 1), IFDRational(int(s * 100), 100))
        gps[1], gps[2] = ("N" if lat >= 0 else "S"), dms(lat)
        gps[3], gps[4] = ("E" if lon >= 0 else "W"), dms(lon)
    return ex.tobytes()


def save_jpeg(img: Image.Image, path: Path, dt: datetime | None, cam=None, place=None,
              quality: int = 90, orientation: int = 1, mtime: datetime | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    kw = {"quality": quality}
    if dt:
        kw["exif"] = exif_bytes(dt, cam, place, orientation)
    img.save(path, "JPEG", **kw)
    t = (mtime or dt or datetime(2020, 1, 1)).timestamp()
    os.utime(path, (t, t))


def set_mtime(path: Path, dt: datetime) -> None:
    os.utime(path, (dt.timestamp(), dt.timestamp()))


def _ffmpeg() -> str | None:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return shutil.which("ffmpeg")


def make_video(path: Path, source: str, size: str, seconds: float, created: datetime, bitrate: str = "1M") -> bool:
    exe = _ffmpeg()
    if not exe:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", f"{source}=size={size}:rate=30",
           "-f", "lavfi", "-i", "sine=frequency=330:sample_rate=44100", "-t", str(seconds),
           "-c:v", "libx264", "-preset", "veryfast", "-b:v", bitrate, "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "96k", "-shortest",
           "-metadata", f"creation_time={created:%Y-%m-%dT%H:%M:%S}Z", str(path)]
    subprocess.run(cmd, check=True, creationflags=CREATE_NO_WINDOW)
    set_mtime(path, created)
    return True


def reencode_video(src: Path, dst: Path, args: list[str], mtime: datetime, start: float = 0.0) -> None:
    """Re-encode ``src`` into ``dst`` (e.g. a messenger-compressed or trimmed copy)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", *(["-ss", f"{start:.2f}"] if start else []),
           "-i", str(src), *args, "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
           "-c:a", "aac", str(dst)]
    subprocess.run(cmd, check=True, creationflags=CREATE_NO_WINDOW)
    set_mtime(dst, mtime)


# --------------------------------------------------------------------------------------
# Library builder
# --------------------------------------------------------------------------------------
BUILD_STEPS = [
    "Creating camera photos…", "Creating large photos and their backups…", "Copying exact duplicates…",
    "Making WhatsApp-style photo copies…", "Shooting bursts…", "Adding blurry shots…",
    "Adding screenshots and downloads…", "Adding an iPhone HEIC photo…", "Adding problem files…",
    "Recording videos…", "Copying a duplicate video…", "Making a compressed video copy…",
    "Making a trimmed video copy…", "Recording an unrelated video…", "Writing the answer key…",
]


def build(dest: Path = DEFAULT_DEST, small: bool = False, videos: bool = True, progress=None) -> dict:
    """Generate the library at ``dest``. ``progress`` is an optional ``(done, total, message)`` callable."""
    step_no = 0

    def step() -> None:
        nonlocal step_no
        if progress is not None:
            progress(step_no, len(BUILD_STEPS), BUILD_STEPS[step_no])
        step_no += 1

    dest = Path(dest)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    exp: dict = {"duplicate_groups": [], "bursts": [], "near_duplicates": [], "blurry": [], "junk": [],
                 "empty_files": [], "empty_folders": [], "corrupt": [], "non_media": [], "rotated": [],
                 "dates": {}, "uncertain_dates": [], "large_duplicates": [], "videos": [], "heic": [],
                 "similar_videos": []}
    seed = 1000
    originals: list[tuple[str, datetime]] = []
    scale = 0.5 if small else 1.0
    W, H = int(1600 * scale), int(1200 * scale)

    def rel(p: Path) -> str:
        return str(p.relative_to(dest))

    # 1. Events from cameras / phones
    step()
    for date_s, name, count, cam, place, folder in EVENTS:
        count = max(2, count // 2) if small else count
        t0 = datetime.fromisoformat(date_s)
        for i in range(count):
            seed += 1
            dt = t0 + timedelta(minutes=7 * i, seconds=seed % 50)
            fname = (f"IMG_{seed:04d}.JPG" if cam == 0 else f"PXL_{dt:%Y%m%d_%H%M%S}{seed % 1000:03d}.jpg"
                     if cam == 1 else f"IMG_{seed:04d}.jpeg")
            p = dest / folder / fname
            orientation = 1
            img = scene(seed, W, H)
            if i == 1 and name in ("Goa trip", "Wedding"):
                # Portrait photo stored sideways with an EXIF rotation flag, like phones do.
                img = scene(seed, H, W).transpose(Image.Transpose.ROTATE_90)
                orientation = 6
                exp["rotated"].append(rel(p))
            save_jpeg(img, p, dt, cam, place, orientation=orientation)
            originals.append((rel(p), dt))
            exp["dates"][rel(p)] = {"date": dt.isoformat(sep=" "), "source": "exif"}

    step()
    # 2. Large (>1.28 MB) originals + exact copies — regression for the sampled-hash bug
    big_n = 2 if small else 4
    for i in range(big_n):
        seed += 1
        dt = datetime(2023, 6, 11, 7, 0) + timedelta(minutes=13 * i)
        p = dest / "DCIM" / "101CANON" / f"IMG_{seed:04d}_HDR.JPG"
        bw, bh = (2400, 1800) if small else (4000, 3000)
        img = scene(seed, bw, bh)
        arr = np.asarray(img, dtype=np.float32) + np.random.default_rng(seed).normal(0, 10, (bh, bw, 3))
        save_jpeg(Image.fromarray(arr.clip(0, 255).astype(np.uint8)), p, dt, 0, "Ladakh", quality=95)
        copy = dest / "Phone Backup" / "2023" / p.name
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, copy)
        set_mtime(copy, datetime(2024, 1, 5, 12, 0))
        exp["duplicate_groups"].append(sorted([rel(p), rel(copy)]))
        exp["large_duplicates"].append(rel(p))
        exp["dates"][rel(p)] = {"date": dt.isoformat(sep=" "), "source": "exif"}

    step()
    # 3. Exact duplicates of normal photos: backups, "(1)" downloads, a triple copy
    picks = originals[2::5][: (3 if small else 6)]
    for j, (r, dt) in enumerate(picks):
        src = dest / r
        group = [r]
        c1 = dest / "Phone Backup" / f"{dt:%Y}" / src.name
        c1.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, c1)
        set_mtime(c1, datetime(2024, 1, 5, 12, j))
        group.append(rel(c1))
        if j % 2 == 0:
            c2 = dest / "Downloads" / f"{src.stem} (1){src.suffix}"
            c2.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, c2)
            group.append(rel(c2))
        exp["duplicate_groups"].append(sorted(group))

    step()
    # 4. Near-duplicates: WhatsApp-style resized, recompressed copies with EXIF stripped
    for j, (r, dt) in enumerate(originals[4::7][: (2 if small else 4)]):
        src = ImageOps.exif_transpose(Image.open(dest / r))
        small_img = src.resize((src.width // 2, src.height // 2), Image.Resampling.LANCZOS)
        wa = dest / "WhatsApp Images" / f"IMG-{dt:%Y%m%d}-WA{j:04d}.jpg"
        save_jpeg(small_img, wa, None, quality=65, mtime=dt + timedelta(days=2))
        exp["near_duplicates"].append({"files": sorted([r, rel(wa)]), "best": r})
        exp["dates"][rel(wa)] = {"date": f"{dt:%Y-%m-%d} 00:00:00", "source": "filename"}

    step()
    # 5. Bursts: 5 frames 1 s apart, slight camera shake, varying blur/exposure. Frame 2 is best.
    bursts = 2 if small else 3
    blur_radius = [2.2, 3.5, 0.0, 1.4, 5.0]
    exposure = [1.0, 0.95, 1.0, 0.55, 1.05]
    for b in range(bursts):
        seed += 1
        t0 = datetime(2023, 6, 12, 6, 30 + b * 10)
        frames = []
        for k in range(5):
            img = scene(seed, W, H, shift=(k * 3 - 6, (k % 2) * 3))
            if blur_radius[k]:
                img = img.filter(ImageFilter.GaussianBlur(blur_radius[k]))
            if exposure[k] != 1.0:
                img = Image.fromarray((np.asarray(img, np.float32) * exposure[k]).clip(0, 255).astype(np.uint8))
            p = dest / "DCIM" / "101CANON" / f"BURST_{seed:04d}_{k + 1}.JPG"
            save_jpeg(img, p, t0 + timedelta(seconds=k), 0, "Ladakh")
            frames.append(rel(p))
        exp["bursts"].append({"files": frames, "best": frames[2]})

    step()
    # 6. Blurry single shots
    for k in range(2 if small else 4):
        seed += 1
        dt = datetime(2022, 11, 3, 21, k * 5)
        p = dest / "Camera Roll" / "2022" / f"PXL_{dt:%Y%m%d_%H%M%S}000.jpg"
        save_jpeg(scene(seed, W, H).filter(ImageFilter.GaussianBlur(7)), p, dt, 1, None)
        exp["blurry"].append(rel(p))
        exp["dates"][rel(p)] = {"date": dt.isoformat(sep=" "), "source": "exif"}

    step()
    # 7. Screenshots and other files dated only by name
    for k in range(2 if small else 4):
        dt = datetime(2024, 2, 10, 10, 10, 10 + k)
        p = dest / "Screenshots" / f"Screenshot {dt:%Y-%m-%d %H%M%S}.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        screenshot(k, 540, 1170).save(p)
        set_mtime(p, datetime(2025, 1, 1))
        exp["dates"][rel(p)] = {"date": dt.isoformat(sep=" "), "source": "filename"}
    for k, dt in enumerate([datetime(2021, 3, 15, 9, 30), datetime(2022, 8, 2, 10, 15, 30)]):
        seed += 1
        name = (f"IMG_{dt:%Y%m%d_%H%M%S}.jpg" if k == 0 else f"WhatsApp Image {dt:%Y-%m-%d} at {dt:%H.%M.%S}.jpeg")
        p = dest / "Downloads" / name
        save_jpeg(scene(seed, W, H), p, None, mtime=datetime(2025, 3, 1))
        exp["dates"][rel(p)] = {"date": dt.isoformat(sep=" "), "source": "filename"}
    seed += 1
    p = dest / "Scans" / "scan_001.jpg"
    save_jpeg(scene(seed, W, H), p, None, mtime=datetime(2020, 5, 5, 12, 0))
    exp["uncertain_dates"].append(rel(p))

    step()
    # 8. HEIC from an iPhone
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
        seed += 1
        dt = datetime(2025, 10, 20, 21, 0)
        p = dest / "iPhone Import" / f"IMG_{seed:04d}.HEIC"
        scene(seed, W, H).save(p, format="HEIF", quality=80, exif=exif_bytes(dt, 2, "Delhi"))
        set_mtime(p, dt)
        exp["heic"].append(rel(p))
        exp["dates"][rel(p)] = {"date": dt.isoformat(sep=" "), "source": "exif"}
    except Exception as e:  # pragma: no cover
        print("HEIC skipped:", e)

    step()
    # 9. Problems: corrupt photo, junk, empty files/folders, non-media
    seed += 1
    full = dest / "Camera Roll" / "2021" / "IMG_9999.jpg"
    save_jpeg(scene(seed, W, H), full, datetime(2021, 3, 16, 12, 0), 1, "Goa")
    data = full.read_bytes()
    full.write_bytes(data[: len(data) * 2 // 5])
    exp["corrupt"].append(rel(full))
    junk = {"DCIM\\100CANON\\Thumbs.db": b"\x00" * 2048, "Camera Roll\\desktop.ini": b"[.ShellClassInfo]\r\n",
            "iPhone Import\\.DS_Store": b"\x00\x00\x00\x01Bud1", "iPhone Import\\._IMG_0001.jpeg": b"\x00\x05\x16\x07" * 64,
            "Downloads\\photo-album.zip.crdownload": b"partial" * 100}
    for r, b in junk.items():
        (dest / r).parent.mkdir(parents=True, exist_ok=True)
        (dest / r).write_bytes(b)
        exp["junk"].append(r)
    for r in ("Downloads\\IMG_0099.jpg", "Camera Roll\\2024\\VID_empty.mp4"):
        (dest / r).parent.mkdir(parents=True, exist_ok=True)
        (dest / r).write_bytes(b"")
        exp["empty_files"].append(r)
    for r in ("New folder", "Old Stuff\\Empty Album"):
        (dest / r).mkdir(parents=True, exist_ok=True)
    exp["empty_folders"] = ["New folder", "Old Stuff", "Old Stuff\\Empty Album"]
    for r, text in {"Documents\\itinerary.txt": "Goa trip itinerary\n", "Documents\\notes.md": "# Notes\n"}.items():
        (dest / r).parent.mkdir(parents=True, exist_ok=True)
        (dest / r).write_text(text)
        exp["non_media"].append(r)

    step()
    # 10. Videos (+ one exact duplicate)
    have_ffmpeg = videos and bool(_ffmpeg())
    if have_ffmpeg:
        specs = [("Camera Roll\\2023\\VID_20230610_090000.mp4", "testsrc2", "640x360", 3, datetime(2023, 6, 10, 9), "800k"),
                 ("iPhone Import\\IMG_5001.MOV", "smptebars", "720x1280", 3, datetime(2025, 10, 20, 20, 30), "1M"),
                 ("Camera Roll\\2024\\VID_20240210_163000.mp4", "testsrc", "1280x720", 4 if small else 6,
                  datetime(2024, 2, 10, 16, 30), "8M")]
        for r, src, size, secs, created, br in specs:
            if make_video(dest / r, src, size, secs, created, br):
                exp["videos"].append(r)
                exp["dates"][r] = {"date": created.isoformat(sep=" "), "source": "metadata"}
    step()
    if have_ffmpeg:
        vdup = dest / "Phone Backup" / "2023" / "VID_20230610_090000.mp4"
        shutil.copy2(dest / specs[0][0], vdup)
        exp["duplicate_groups"].append(sorted([specs[0][0], rel(vdup)]))

    # 11. Similar videos: a messenger-compressed, downscaled copy and a slightly trimmed copy.
    # The exact duplicate above joins the trimmed group but must be collapsed away.
    step()
    if have_ffmpeg:
        orig = specs[2][0]
        wa = dest / "WhatsApp Video" / "VID-20240210-WA0001.mp4"
        reencode_video(dest / orig, wa, ["-vf", "scale=640:360", "-b:v", "300k", "-b:a", "64k",
                                         "-map_metadata", "-1"], datetime(2024, 2, 12, 9, 0))
        exp["videos"].append(rel(wa))
        exp["similar_videos"].append({"files": sorted([orig, rel(wa)]), "best": orig})
    step()
    if have_ffmpeg:
        orig = specs[0][0]
        trimmed = dest / "Videos" / "Edited" / "VID_20230610_090000_trim.mp4"
        reencode_video(dest / orig, trimmed, ["-b:v", "400k", "-b:a", "64k"], datetime(2023, 6, 15, 18, 0),
                       start=0.3)
        exp["videos"].append(rel(trimmed))
        exp["similar_videos"].append({"files": sorted([orig, rel(trimmed)]), "best": orig})
    # An unrelated clip as long as the testsrc video; it must not match anything.
    step()
    if have_ffmpeg:
        r, created = "Camera Roll\\2024\\VID_20240211_101500.mp4", datetime(2024, 2, 11, 10, 15)
        if make_video(dest / r, "mandelbrot", "640x360", 4 if small else 6, created, "1M"):
            exp["videos"].append(r)
            exp["dates"][r] = {"date": created.isoformat(sep=" "), "source": "metadata"}
    exp["similar_videos"].sort(key=lambda g: g["files"])

    step()
    exp["duplicate_groups"].sort()
    exp["non_media"].append("expected.json")
    files = [p for p in dest.rglob("*") if p.is_file()]
    exp["total_files"] = len(files) + 1  # + expected.json itself
    exp["total_bytes"] = sum(p.stat().st_size for p in files)
    (dest / "expected.json").write_text(json.dumps(exp, indent=2))
    if progress is not None:
        progress(len(BUILD_STEPS), len(BUILD_STEPS), "Sample library ready")
    return exp


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dest", nargs="?", default=str(DEFAULT_DEST))
    ap.add_argument("--small", action="store_true", help="fewer, smaller images (fast tests)")
    ap.add_argument("--no-video", action="store_true")
    a = ap.parse_args(argv)
    t = datetime.now()
    exp = build(Path(a.dest), small=a.small, videos=not a.no_video)
    secs = (datetime.now() - t).total_seconds()
    print(f"Built {exp['total_files']} files ({exp['total_bytes'] / 1e6:.1f} MB) in {a.dest} [{secs:.1f}s]")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
