"""iPhone / iPad backups (iTunes or Apple Devices): find, read and copy files out safely.

Design (compared with community parsers such as avibrazil/iOSbackup and jsharkey13/iphone_backup_decrypt):

- The backup is never modified. ``Manifest.db`` is opened as an *immutable* read-only SQLite URI, so
  no journal/WAL side files are created next to it, and backup files are only opened for reading.
- Each file's real size and last-modified time come from the catalogue's ``file`` record (an
  NSKeyedArchiver MBFile plist), so copies get the photo's original date rather than the backup's,
  and nothing has to be stat-ed before copying.
- Encrypted backups are detected up front (they would otherwise be copied as unreadable data).
- Copies are written to a ``.part`` file, size-checked and then renamed, so an interruption never
  leaves a half-written file under the real name. Existing files are never overwritten; clashing names
  (including names that differ only by case) get " (2)", " (3)"… suffixes.
- Progress is resumable: finished files are recorded in ``<destination>/.memoria/ios_backup_state.sqlite``.
- Reads are rationed per drive (see ``disk_speed``) and copied in backup order for locality.
- "Only new" mode skips files whose content is already in a Memoria library (size, then full hash).
"""
from __future__ import annotations

import contextlib
import os
import plistlib
import re
import shutil
import sqlite3
import tempfile
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional

import xxhash

from . import activity, config, disk_speed
from .hashing import full_hash
from .progress import Progress

CHUNK = 4 * 1024 * 1024
STATE_NAME = "ios_backup_state.sqlite"
SIDE_CAR_EXT = {".aae"}

CATEGORIES: dict[str, tuple[str, str, bool]] = {
    # key: (title, help text, is media)
    "camera_roll": ("Photos & videos (Camera Roll)", "Everything in the iPhone's camera roll, with Live Photo pairs.", True),
    "photo_edits": ("Edited photo versions", "Full-size renders of photos edited on the phone.", True),
    "whatsapp_media": ("WhatsApp photos & videos", "Media sent and received in WhatsApp chats.", True),
    "messages": ("Message attachments", "Photos, videos and files from Messages (SMS/iMessage).", True),
    "voice_memos": ("Voice memos", "Recordings from the Voice Memos app.", False),
    "app_documents": ("App documents", "Files apps keep in their Documents folders.", False),
    "whatsapp_data": ("WhatsApp chats & data", "Chat database and app data (not readable as photos).", False),
    "apps": ("Other app data", "Settings, caches and databases of installed apps.", False),
    "system": ("Device & system files", "Settings, contacts/call databases, health and other system data.", False),
}
MEDIA_CATEGORIES = tuple(k for k, v in CATEGORIES.items() if v[2])

KNOWN_APPS = {
    "net.whatsapp.WhatsApp": "WhatsApp",
    "com.microsoft.Office.Word": "Microsoft Word",
    "com.microsoft.Office.Excel": "Microsoft Excel",
    "com.microsoft.Office.Powerpoint": "Microsoft PowerPoint",
    "com.microsoft.Office.Outlook": "Microsoft Outlook",
    "com.microsoft.skype.teams": "Microsoft Teams",
    "com.google.chrome.ios": "Google Chrome",
    "com.openai.chat": "ChatGPT",
    "com.burbn.instagram": "Instagram",
    "com.spotify.client": "Spotify",
    "com.netflix.Netflix": "Netflix",
    "ph.telegra.Telegraph": "Telegram",
    "org.whispersystems.signal": "Signal",
}
_WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_MAX_COMPONENT = 200


class BackupError(Exception):
    """A backup can't be used (missing catalogue, encrypted, unreadable)."""


# --------------------------------------------------------------------------- finding backups
def default_backup_dirs() -> list[Path]:
    """Folders where iTunes (desktop and Microsoft Store) and Apple Devices keep backups."""
    dirs = []
    if os.name == "nt":
        for base, sub in (("APPDATA", r"Apple Computer\MobileSync\Backup"),
                          ("USERPROFILE", r"Apple\MobileSync\Backup"),
                          ("USERPROFILE", r"AppData\Roaming\Apple Computer\MobileSync\Backup")):
            if os.environ.get(base):
                dirs.append(Path(os.environ[base]) / sub)
    else:
        dirs.append(Path.home() / "Library" / "Application Support" / "MobileSync" / "Backup")
    unique = []
    for d in dirs:
        if d not in unique:
            unique.append(d)
    return unique


@dataclass
class BackupInfo:
    path: Path
    udid: str
    device_name: str = "iPhone"
    product_type: str = ""
    ios_version: str = ""
    serial: str = ""
    last_backup: Optional[datetime] = None
    encrypted: bool = False
    complete: Optional[bool] = None

    @property
    def label(self) -> str:
        when = self.last_backup.strftime("%d %b %Y %H:%M") if self.last_backup else "unknown date"
        model = f" ({self.product_type})" if self.product_type else ""
        return f"{self.device_name}{model} · iOS {self.ios_version or '?'} · {when}"

    @property
    def folder_name(self) -> str:
        when = self.last_backup.strftime("%Y-%m-%d") if self.last_backup else "backup"
        return sanitize_component(f"{self.device_name} {when}")


def _load_plist(path: Path) -> dict:
    try:
        with open(config.longpath(path), "rb") as f:
            value = plistlib.load(f)
        return value if isinstance(value, dict) else {}
    except (OSError, plistlib.InvalidFileException, ValueError, TypeError):
        return {}


def read_backup(path: str | Path) -> BackupInfo:
    """Device details for the backup folder at ``path``. Raises BackupError if it isn't a backup."""
    path = Path(path)
    if not (path / "Manifest.db").is_file():
        if (path / "Manifest.mbdb").is_file():
            raise BackupError("This backup was made by iOS 9 or older, which uses a format Memoria can't read.")
        raise BackupError(f"No iPhone backup catalogue (Manifest.db) was found in {path}.")
    info, manifest, status = (_load_plist(path / n) for n in ("Info.plist", "Manifest.plist", "Status.plist"))
    lockdown = manifest.get("Lockdown") if isinstance(manifest.get("Lockdown"), dict) else {}
    when = info.get("Last Backup Date") or status.get("Date") or manifest.get("Date")
    if isinstance(when, datetime) and when.tzinfo is not None:
        when = when.astimezone().replace(tzinfo=None)
    elif not isinstance(when, datetime):
        try:
            when = datetime.fromtimestamp((path / "Manifest.db").stat().st_mtime)
        except OSError:
            when = None
    state = status.get("SnapshotState")
    return BackupInfo(
        path=path, udid=path.name,
        device_name=str(info.get("Device Name") or lockdown.get("DeviceName") or "iPhone"),
        product_type=str(info.get("Product Type") or lockdown.get("ProductType") or ""),
        ios_version=str(info.get("Product Version") or lockdown.get("ProductVersion") or ""),
        serial=str(info.get("Serial Number") or lockdown.get("SerialNumber") or ""),
        last_backup=when, encrypted=bool(manifest.get("IsEncrypted", False)),
        complete=None if state is None else state == "finished")


def find_backups(extra_dirs: Iterable[str | Path] = ()) -> list[BackupInfo]:
    """Backups in the default folders (and ``extra_dirs``), newest first. Unreadable folders are skipped."""
    found, seen = [], set()
    for root in [*default_backup_dirs(), *map(Path, extra_dirs)]:
        candidates = [root] if (root / "Manifest.db").is_file() else []
        try:
            candidates += [p for p in root.iterdir() if p.is_dir()]
        except OSError:
            pass
        for folder in candidates:
            key = os.path.normcase(str(folder.resolve()))
            if key in seen:
                continue
            seen.add(key)
            try:
                found.append(read_backup(folder))
            except BackupError:
                continue
    found.sort(key=lambda b: b.last_backup or datetime.min, reverse=True)
    return found


# --------------------------------------------------------------------------- catalogue
@dataclass
class Entry:
    file_id: str
    domain: str
    relative_path: str
    size: int
    mtime: Optional[float]
    category: str
    dest_rel: str

    @property
    def is_media(self) -> bool:
        ext = os.path.splitext(self.relative_path)[1].lower()
        return ext in config.MEDIA_EXT or ext in SIDE_CAR_EXT


def _file_meta(blob) -> tuple[Optional[int], Optional[float]]:
    """(size, last-modified Unix time) from a Manifest.db ``file`` record; (None, None) if unreadable."""
    if not blob:
        return None, None
    try:
        archive = plistlib.loads(bytes(blob))
        objects = archive["$objects"]
        top = archive["$top"]["root"]
        record = objects[top.data if isinstance(top, plistlib.UID) else int(top)]
    except Exception:
        return None, None
    size = record.get("Size")
    size = int(size) if isinstance(size, int) and size >= 0 else None
    mtime = record.get("LastModified")
    if not isinstance(mtime, (int, float)) or not 631152000 <= mtime <= time.time() + 366 * 86400:  # 1990..next year
        mtime = None
    return size, (float(mtime) if mtime is not None else None)


def _open_manifest(backup: BackupInfo) -> sqlite3.Connection:
    if backup.encrypted:
        raise BackupError("This backup is encrypted (iTunes/Apple Devices “Encrypt local backup”). Memoria can't "
                          "read encrypted backups. Make an unencrypted backup, or decrypt it with a dedicated tool first.")
    uri = Path(backup.path, "Manifest.db").resolve().as_uri() + "?mode=ro&immutable=1"
    try:
        conn = sqlite3.connect(uri, uri=True)
        conn.execute("SELECT 1 FROM Files LIMIT 1").fetchall()
    except sqlite3.DatabaseError as error:
        raise BackupError(f"The backup catalogue can't be read ({error}). The backup may be encrypted, "
                          "incomplete or damaged.") from None
    return conn


def sanitize_component(name: str) -> str:
    """One path segment that is valid on Windows; keeps the extension when shortening."""
    cleaned = _ILLEGAL.sub("_", name).strip(" .") or "_"
    if cleaned.split(".")[0].upper() in _WINDOWS_RESERVED:
        cleaned = "_" + cleaned
    if len(cleaned) > _MAX_COMPONENT:
        stem, ext = os.path.splitext(cleaned)
        ext = ext if len(ext) <= 16 else ""
        cleaned = stem[:_MAX_COMPONENT - len(ext)].rstrip(" .") + ext
    return cleaned


def safe_relative(path: str) -> str:
    """A relative path that can't escape its folder (no drive, no '..', valid Windows names)."""
    parts = [p for p in path.replace("\\", "/").split("/") if p not in ("", ".", "..")]
    return os.path.join(*(sanitize_component(p) for p in parts)) if parts else "unnamed"


def _app_name(bundle: str) -> str:
    for bundle_id, name in KNOWN_APPS.items():
        if bundle_id.lower() in bundle.lower():
            return name
    words = [p for p in bundle.split(".") if p.lower() not in ("com", "org", "net", "io", "ios", "group", "app", "shared")]
    return " ".join(w[:1].upper() + w[1:] for w in words) or bundle


def classify(domain: str, relative_path: str) -> tuple[str, str]:
    """(category, destination path relative to the output folder) for one backup file."""
    rel = relative_path.replace("\\", "/").strip("/")
    low = domain.lower()

    def under(prefix: str) -> Optional[str]:
        return rel[len(prefix):].strip("/") if rel.startswith(prefix) else None

    if domain == "CameraRollDomain":
        if (sub := under("Media/DCIM/")) is not None:
            return "camera_roll", f"Camera Roll/{sub}"
        if "/Mutations/" in f"/{rel}" and re.search(r"FullSizeRender\.\w+$", rel):
            return "photo_edits", f"Edited Photos/{under('Media/PhotoData/Mutations/') or rel}"
        return "system", f"System & Device/Photo Library Data/{under('Media/') or rel}"
    if "whatsapp" in low:
        if "Message/Media/" in rel:
            return "whatsapp_media", f"WhatsApp/Media/{rel.split('Message/Media/', 1)[1]}"
        return "whatsapp_data", f"WhatsApp/Data/{rel}"
    if domain == "MediaDomain":
        if "SMS/Attachments/" in rel:
            return "messages", f"Messages/Attachments/{rel.split('SMS/Attachments/', 1)[1]}"
        if "Recordings/" in rel:
            return "voice_memos", f"Voice Memos/{rel.split('Recordings/', 1)[1]}"
        return "system", f"System & Device/Media/{rel}"
    if "voicememos" in low and "Recordings/" in rel:
        return "voice_memos", f"Voice Memos/{rel.split('Recordings/', 1)[1]}"
    for prefix in ("AppDomainGroup-group.", "AppDomainPlugin-", "AppDomainGroup-", "AppDomain-"):
        if domain.startswith(prefix):
            app = _app_name(domain[len(prefix):])
            if (sub := under("Documents/")) is not None:
                return "app_documents", f"Apps/{app}/Documents/{sub}"
            return "apps", f"Apps/{app}/Data/{rel}"
    names = {"HomeDomain": "Home", "SystemPreferencesDomain": "Preferences", "WirelessDomain": "Wireless",
             "KeychainDomain": "Keychain", "ManagedPreferencesDomain": "Managed Preferences",
             "RootDomain": "Root", "DatabaseDomain": "Databases", "HealthDomain": "Health"}
    return "system", f"System & Device/{names.get(domain, domain)}/{rel}"


def list_files(backup: BackupInfo, progress: Optional[Progress] = None) -> list[Entry]:
    """Every regular file in the backup, in backup order (fileID), with real size and date."""
    progress = progress or Progress()
    conn = _open_manifest(backup)
    try:
        total = conn.execute("SELECT COUNT(*) FROM Files WHERE flags=1").fetchone()[0]
        entries = []
        rows = conn.execute("SELECT fileID, domain, relativePath, file FROM Files WHERE flags=1 ORDER BY fileID")
        for n, (file_id, domain, rel, blob) in enumerate(rows, 1):
            if n % 2000 == 0:
                progress.update(n, total, f"Reading the backup catalogue… {n:,} of {total:,} files")
            if not isinstance(file_id, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", file_id):
                continue  # not a backup file name; never build paths from it
            size, mtime = _file_meta(blob)
            category, dest = classify(domain or "", rel or "")
            entries.append(Entry(file_id.lower(), domain or "", rel or "", -1 if size is None else size,
                                 mtime, category, dest))
    finally:
        conn.close()
    return entries


def summarize(entries: Iterable[Entry], media_only: bool = False) -> dict[str, tuple[int, int]]:
    """{category: (files, bytes)}; files with unknown size count as 0 bytes."""
    out: dict[str, list[int]] = {k: [0, 0] for k in CATEGORIES}
    for e in entries:
        if media_only and not e.is_media:
            continue
        out[e.category][0] += 1
        out[e.category][1] += max(0, e.size)
    return {k: (v[0], v[1]) for k, v in out.items()}


# --------------------------------------------------------------------------- extraction
@dataclass
class ExtractResult:
    destination: Path
    copied: int = 0
    copied_bytes: int = 0
    resumed: int = 0
    already_in_library: int = 0
    renamed: int = 0
    missing: int = 0
    failed: int = 0
    size_mismatches: int = 0
    errors: list[str] = field(default_factory=list)
    placed: dict[str, str] = field(default_factory=dict)    # backup file id → path under the destination
    matched: dict[str, int] = field(default_factory=dict)   # backup file id → library file already holding it
    recently_deleted: int = 0                                # left out: in the iPhone's Recently Deleted
    details: Optional[dict[str, int]] = None                 # what apply_photos_details kept

    def note(self, message: str) -> None:
        if len(self.errors) < 200:
            self.errors.append(message)


class _State:
    """Resumable record of finished files, committed in batches (not one disk flush per file)."""

    def __init__(self, dest: Path):
        app = dest / config.APP_DIR_NAME
        app.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(app / STATE_NAME), check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS done (file_id TEXT PRIMARY KEY, dest_rel TEXT NOT NULL, "
                          "size INTEGER NOT NULL, chash TEXT, finished_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        self.conn.commit()
        self.pending: list[tuple] = []
        self.last = time.monotonic()

    def finished(self) -> dict[str, tuple[str, int]]:
        return {r[0]: (r[1], r[2]) for r in self.conn.execute("SELECT file_id, dest_rel, size FROM done")}

    def add(self, file_id: str, dest_rel: str, size: int, chash: Optional[str]) -> None:
        self.pending.append((file_id, dest_rel, size, chash))
        if len(self.pending) >= 500 or time.monotonic() - self.last >= 2:
            self.flush()

    def flush(self) -> None:
        if self.pending:
            self.conn.executemany("INSERT OR REPLACE INTO done (file_id, dest_rel, size, chash) VALUES (?,?,?,?)",
                                  self.pending)
            self.conn.commit()
            self.pending.clear()
        self.last = time.monotonic()

    def close(self) -> None:
        self.flush()
        self.conn.close()


def _source(backup: BackupInfo, entry: Entry) -> Path:
    return backup.path / entry.file_id[:2] / entry.file_id


def _plan_names(entries: list[Entry], dest: Path, finished: dict[str, tuple[str, int]]) -> tuple[dict[str, str], set[str]]:
    """Unique destination per file, plus ids already present from an interrupted run.

    Earlier runs keep their names. A file already at the planned name with the catalogue's size and
    date is one we copied before the run was interrupted, so it is adopted instead of copied again.
    Other clashes (in any letter case) get " (2)", " (3)"…
    """
    taken: set[str] = {os.path.normcase(rel) for rel, _ in finished.values()}
    names: dict[str, str] = {}
    adopted: set[str] = set()
    for e in entries:
        if e.file_id in finished:
            names[e.file_id] = finished[e.file_id][0]
            continue
        rel = safe_relative(e.dest_rel)
        stem, ext = os.path.splitext(rel)
        n = 1
        while os.path.normcase(rel) in taken or os.path.lexists(config.longpath(dest / rel)):
            if os.path.normcase(rel) not in taken and _is_previous_copy(dest / rel, e):
                adopted.add(e.file_id)
                break
            n += 1
            rel = f"{stem} ({n}){ext}"
        taken.add(os.path.normcase(rel))
        names[e.file_id] = rel
    return names, adopted


def _is_previous_copy(path: Path, e: Entry) -> bool:
    if e.size < 0 or e.mtime is None:
        return False
    try:
        st = os.stat(config.longpath(path))
    except OSError:
        return False
    return st.st_size == e.size and abs(st.st_mtime - e.mtime) < 2


def _copy(src: Path, final: Path, expected: int, mtime: Optional[float], progress: Progress,
          on_bytes) -> tuple[int, str, bool]:
    """Copy via ``.part`` + rename; returns (bytes, xxh3-128, size differs from catalogue).

    Never replaces an existing file. A size that disagrees with the catalogue (an interrupted or
    damaged backup) is still copied, so no data is lost, and reported to the caller.
    """
    final.parent.mkdir(parents=True, exist_ok=True)
    part = final.with_name(final.name + ".part")
    digest = xxhash.xxh3_128()
    copied = 0
    try:
        with open(config.longpath(src), "rb", buffering=0) as rf, open(config.longpath(part), "wb") as wf:
            buf = bytearray(CHUNK)
            view = memoryview(buf)
            while True:
                progress.check()
                n = rf.readinto(buf)
                if not n:
                    break
                wf.write(view[:n])
                digest.update(view[:n])
                copied += n
                on_bytes(n)
        if os.path.lexists(config.longpath(final)):
            raise FileExistsError(f"{final} appeared while copying")
        os.rename(config.longpath(part), config.longpath(final))
    except BaseException:
        with contextlib.suppress(OSError):
            os.remove(config.longpath(part))
        raise
    stamp = mtime if mtime is not None else os.stat(config.longpath(src)).st_mtime
    with contextlib.suppress(OSError):
        os.utime(config.longpath(final), (stamp, stamp))
    return copied, digest.hexdigest(), expected >= 0 and copied != expected


def _library_matches(lib, backup: BackupInfo, entries: list[Entry], progress: Progress) -> dict[str, int]:
    """Backup file id → the library file that already holds its exact content (size, then full hash)."""
    by_size: dict[int, list] = defaultdict(list)
    for row in lib.readable_files("size > 0"):
        by_size[row["size"]].append(row)
    candidates = [e for e in entries if e.size > 0 and e.size in by_size]
    if not candidates:
        return {}
    lib_todo = {row["id"]: row for e in candidates for row in by_size[e.size] if not row["chash"]}
    lib_hashes: dict[int, Optional[str]] = {row["id"]: row["chash"] for e in candidates for row in by_size[e.size]}
    src_gate = disk_speed.io_gate(backup.path)
    lib_gates = disk_speed.root_gates(lib)
    total = len(candidates) + len(lib_todo)
    done = 0

    def lib_hash(row):
        from .roots import split_key
        with lib_gates.get(split_key(row["rel_path"])[0]) or contextlib.nullcontext():
            return row["id"], full_hash(lib.abspath(row["rel_path"]))

    def src_hash(e: Entry):
        with src_gate:
            return e.file_id, full_hash(_source(backup, e))

    workers = max(1, min(config.WORKERS, disk_speed.detect_disk(backup.path)["workers"]))
    found: dict[str, int] = {}
    with activity.pool("Comparing with library", workers), ThreadPoolExecutor(max_workers=workers) as pool:
        updates = []
        for fid, h in pool.map(lib_hash, sorted(lib_todo.values(), key=lambda r: r["rel_path"].lower())):
            lib_hashes[fid] = h
            if h:
                updates.append((fid, None, h))
            done += 1
            progress.update(done, total, f"Checking which photos are already in the library… {done:,} of {total:,}")
        if updates:
            lib.set_hashes(updates)
        sizes = {e.file_id: e.size for e in candidates}
        for file_id, h in pool.map(src_hash, candidates):
            done += 1
            match = next((row["id"] for row in by_size[sizes[file_id]] if h and lib_hashes.get(row["id"]) == h), None)
            if match is not None:
                found[file_id] = match
            progress.update(done, total, f"Checking which photos are already in the library… {done:,} of {total:,}")
    return found


def extract(backup: BackupInfo, destination: str | Path, categories: Iterable[str], *,
            progress: Optional[Progress] = None, media_only: bool = False, library=None,
            entries: Optional[list[Entry]] = None) -> ExtractResult:
    """Copy the chosen categories out of ``backup`` into ``destination`` (resumable, never overwrites).

    ``library``: skip files whose content the Memoria library already holds ("only new").
    ``media_only``: only photo/video files (and their .AAE edit sidecars).
    """
    progress = progress or Progress()
    dest = Path(destination).resolve()
    source_root = backup.path.resolve()
    if dest == source_root or source_root in dest.parents:
        raise BackupError("Choose a destination outside the backup folder. The backup is never changed.")
    chosen = set(categories)
    if unknown := chosen - set(CATEGORIES):
        raise ValueError(f"Unknown backup categories: {', '.join(sorted(unknown))}")
    if entries is None:
        entries = list_files(backup, progress.step(0, 3, "Reading the backup"))
    todo = [e for e in entries if e.category in chosen and (not media_only or e.is_media)]
    result = ExtractResult(destination=dest)
    dest.mkdir(parents=True, exist_ok=True)
    state = _State(dest)
    try:
        finished = state.finished()
        skip: set[str] = set()
        for e in todo:
            if e.file_id in finished:
                rel, size = finished[e.file_id]
                path = config.longpath(dest / rel)
                if os.path.isfile(path) and os.path.getsize(path) == size:
                    skip.add(e.file_id)
                    result.resumed += 1
                    result.placed[e.file_id] = rel
                else:
                    finished.pop(e.file_id)  # deleted or changed since: copy again under the same rules
        todo = [e for e in todo if e.file_id not in skip]
        if library is not None and todo:
            in_library = _library_matches(library, backup, todo, progress.step(1, 3, "Comparing with your library"))
            result.already_in_library = len(in_library)
            result.matched = in_library
            todo = [e for e in todo if e.file_id not in in_library]
        names, adopted = _plan_names(todo, dest, finished)
        for e in todo:
            if e.file_id in adopted:
                state.add(e.file_id, names[e.file_id], e.size, None)
                result.placed[e.file_id] = names[e.file_id]
        result.resumed += len(adopted)
        todo = [e for e in todo if e.file_id not in adopted]
        need = sum(max(0, e.size) for e in todo)
        free = shutil.disk_usage(dest).free
        if need > free * 0.99:
            raise BackupError(f"Not enough free space: about {need / 2**30:.1f} GB is needed and "
                              f"{free / 2**30:.1f} GB is free at {dest}.")
        step = progress.step(2, 3, "Copying")
        total_bytes, total_files = need, len(todo)
        counters = {"files": 0, "bytes": 0}
        count_lock = threading.Lock()
        src_gate = disk_speed.io_gate(backup.path)
        dest_gate = disk_speed.io_gate(dest)
        same_drive = src_gate is dest_gate
        workers = max(1, min(config.WORKERS, src_gate.plan["workers"], dest_gate.plan["workers"]))

        def report(name: str = "") -> None:
            step.update(counters["bytes"], total_bytes or 1,
                        f"{counters['files']:,} of {total_files:,} files" + (f" · {name}" if name else ""),
                        detail={"items": (counters["files"], total_files),
                                "bytes": (counters["bytes"], total_bytes), "unit": "file"})

        def add_bytes(n: int) -> None:
            with count_lock:
                counters["bytes"] += n
            report()  # throttled by Progress; keeps a multi-GB video's copy moving in the task bar

        def work(e: Entry):
            src = _source(backup, e)
            final = dest / names[e.file_id]
            if not os.path.isfile(config.longpath(src)):
                return e, None, "missing"
            gates = (src_gate,) if same_drive else (src_gate, dest_gate)
            with contextlib.ExitStack() as stack:
                for gate in gates:
                    stack.enter_context(gate)
                try:
                    copied = _copy(src, final, e.size, e.mtime, step, add_bytes)
                except OSError as error:
                    return e, None, f"{type(error).__name__}: {error}"
            if copied[2]:
                return e, copied, f"size: copied {copied[0]:,} bytes but the backup catalogue says {e.size:,}"
            return e, copied, None

        report()
        with activity.pool("Copying", workers), ThreadPoolExecutor(max_workers=workers) as pool:
            try:
                for e, copied, problem in pool.map(work, todo):
                    counters["files"] += 1
                    if copied is not None:
                        result.copied += 1
                        result.copied_bytes += copied[0]
                        if names[e.file_id] != safe_relative(e.dest_rel):
                            result.renamed += 1
                        state.add(e.file_id, names[e.file_id], copied[0], copied[1])
                        result.placed[e.file_id] = names[e.file_id]
                    if problem == "missing":
                        result.missing += 1
                        result.note(f"{e.domain}/{e.relative_path}: not present in the backup folder")
                    elif problem and problem.startswith("size:"):
                        result.size_mismatches += 1
                        result.note(f"{e.domain}/{e.relative_path}: {problem[5:].strip()}")
                    elif problem:
                        result.failed += 1
                        result.note(f"{e.domain}/{e.relative_path}: {problem}")
                    report(os.path.basename(names[e.file_id]))
            except BaseException:
                pool.shutdown(wait=True, cancel_futures=True)
                raise
        step.update(1, 1, "Copy complete", force=True)
    finally:
        state.close()
    return result


def default_library_folder(lib, backup: BackupInfo) -> Path:
    """Where a library import goes: ``<library>/iPhone backups/<device> <date>``."""
    return Path(lib.root) / "iPhone backups" / backup.folder_name


# --------------------------------------------------------------------------- iPhone Photos library
# Photos.sqlite is Core Data: ZASSET (ZGENERICASSET before iOS 14) holds each photo, ZGENERICALBUM the
# albums, and a join table whose number varies by iOS version (Z_26ASSETS, Z_28ASSETS…) links them.
PHOTOS_DB = "Media/PhotoData/Photos.sqlite"
APPLE_EPOCH = 978307200          # 2001-01-01 UTC, Core Data's time zero
USER_ALBUM = 2                   # ZGENERICALBUM.ZKIND of albums the user made
HIDDEN_ALBUM = "Hidden on iPhone"


@dataclass(frozen=True)
class PhotoInfo:
    taken: Optional[datetime] = None
    favorite: bool = False
    hidden: bool = False
    trashed: bool = False
    albums: tuple[str, ...] = ()


def _table_columns(conn, table: str) -> list[str]:
    return [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')]


def _apple_date(seconds, offset) -> Optional[datetime]:
    from . import dates
    if not isinstance(seconds, (int, float)):
        return None
    try:
        utc = datetime.fromtimestamp(seconds + APPLE_EPOCH, timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None
    # The phone's time zone when the photo was taken; otherwise this PC's.
    if isinstance(offset, (int, float)) and abs(offset) <= 14 * 3600:
        local = (utc + timedelta(seconds=offset)).replace(tzinfo=None)
    else:
        local = utc.astimezone().replace(tzinfo=None)
    return dates._plausible(local.replace(microsecond=0))


def _album_names(conn, tables: dict[str, str]) -> dict[int, list[str]]:
    album = tables.get("ZGENERICALBUM")
    if not album:
        return {}
    cols = {c.upper() for c in _table_columns(conn, album)}
    if "ZTITLE" not in cols:
        return {}
    where = [w for c, w in (("ZKIND", f"ZKIND={USER_ALBUM}"), ("ZTRASHEDSTATE", "COALESCE(ZTRASHEDSTATE,0)=0"))
             if c in cols]
    titles = {pk: " ".join(str(t).split()) for pk, t in conn.execute(
        f'SELECT Z_PK, ZTITLE FROM "{album}"' + (" WHERE " + " AND ".join(where) if where else ""))
        if t and str(t).strip()}
    for name in tables.values():
        if not re.fullmatch(r"Z_\d+ASSETS", name, re.I):
            continue
        cols = _table_columns(conn, name)
        albums_col = next((c for c in cols if re.fullmatch(r"Z_\d+ALBUMS", c, re.I)), None)
        assets_col = next((c for c in cols if re.fullmatch(r"Z_\d+ASSETS", c, re.I)), None)
        if albums_col and assets_col:
            out: dict[int, list[str]] = defaultdict(list)
            for album_pk, asset_pk in conn.execute(f'SELECT "{albums_col}", "{assets_col}" FROM "{name}"'):
                if album_pk in titles:
                    out[asset_pk].append(titles[album_pk])
            return out
    return {}


def _read_photos(conn) -> dict[tuple[str, str], PhotoInfo]:
    tables = {r[0].upper(): r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    asset = tables.get("ZASSET") or tables.get("ZGENERICASSET")
    if not asset:
        return {}
    cols = {c.upper() for c in _table_columns(conn, asset)}
    if not {"Z_PK", "ZDIRECTORY", "ZFILENAME"} <= cols:
        return {}
    offsets = {}
    extra = tables.get("ZADDITIONALASSETATTRIBUTES")
    if extra and {"ZASSET", "ZTIMEZONEOFFSET"} <= {c.upper() for c in _table_columns(conn, extra)}:
        offsets = dict(conn.execute(f'SELECT ZASSET, ZTIMEZONEOFFSET FROM "{extra}" WHERE ZTIMEZONEOFFSET IS NOT NULL'))
    albums_of = _album_names(conn, tables)
    pick = ", ".join(c if c in cols else "NULL" for c in ("ZDATECREATED", "ZFAVORITE", "ZHIDDEN", "ZTRASHEDSTATE"))
    out = {}
    for pk, directory, filename, created, favorite, hidden, trashed in conn.execute(
            f'SELECT Z_PK, ZDIRECTORY, ZFILENAME, {pick} FROM "{asset}"'):
        if not directory or not filename:
            continue
        key = (str(directory).replace("\\", "/").strip("/").lower(), os.path.splitext(str(filename))[0].lower())
        out[key] = PhotoInfo(_apple_date(created, offsets.get(pk)), bool(favorite), bool(hidden), bool(trashed),
                             tuple(dict.fromkeys(albums_of.get(pk, ()))))
    return out


def read_photos_library(backup: BackupInfo, entries: list[Entry]) -> dict[tuple[str, str], PhotoInfo]:
    """What the iPhone's Photos app knew about each camera-roll item: favourite, hidden, Recently Deleted,
    albums and the date Photos shows. Read from a temporary copy (the backup is never opened for writing).
    Empty when the backup has no readable Photos library."""
    by_path = {e.relative_path: e for e in entries if e.domain == "CameraRollDomain"}
    if PHOTOS_DB not in by_path:
        return {}
    with tempfile.TemporaryDirectory(prefix="memoria-photos-") as tmp:
        for suffix in ("", "-wal"):
            e = by_path.get(PHOTOS_DB + suffix)
            src = _source(backup, e) if e is not None else None
            if src is not None and os.path.isfile(config.longpath(src)):
                shutil.copyfile(config.longpath(src), os.path.join(tmp, "Photos.sqlite" + suffix))
        copy = os.path.join(tmp, "Photos.sqlite")
        if not os.path.isfile(copy):
            return {}
        try:
            conn = sqlite3.connect(copy)
            try:
                return _read_photos(conn)
            finally:
                conn.close()
        except sqlite3.DatabaseError:
            return {}


def photo_info(entry: Entry, photos: dict[tuple[str, str], PhotoInfo]) -> Optional[PhotoInfo]:
    """The Photos details for a camera-roll file; a Live Photo's video shares its photo's details."""
    rel = entry.relative_path.replace("\\", "/")
    if not photos or entry.domain != "CameraRollDomain" or not rel.startswith("Media/DCIM/") or "/" not in rel[11:]:
        return None
    folder, name = rel[len("Media/"):].rsplit("/", 1)
    return photos.get((folder.lower(), os.path.splitext(name)[0].lower()))


def apply_photos_details(lib, destination: str | Path, entries: list[Entry], result: ExtractResult,
                         photos: dict[tuple[str, str], PhotoInfo]) -> dict[str, int]:
    """Give imported photos (and library photos the import matched) their iPhone favourites, albums,
    Hidden album and Photos date. Catalogue only; files are never edited. Needs a scan first so newly
    copied files have catalogue rows. Safe to repeat: albums are reused by name, favourites only added."""
    from . import albums as album_engine, organisation
    dest = Path(destination).resolve()
    favourites: list[int] = []
    dated: list[tuple[str, int, int]] = []
    grouped: dict[str, list[int]] = defaultdict(list)
    for e in entries:
        info = photo_info(e, photos)
        if info is None or info.trashed:
            continue
        file_id, new = result.matched.get(e.file_id), False
        if file_id is None and e.file_id in result.placed:
            row = lib.file_by_rel(lib.rel(dest / result.placed[e.file_id]))
            file_id, new = (row["id"] if row is not None else None), True
        if file_id is None:
            continue
        if info.favorite:
            favourites.append(file_id)
        if info.taken:
            dated.append((info.taken.isoformat(sep=" "), file_id, int(new)))
        for name in info.albums:
            grouped[name].append(file_id)
        if info.hidden:
            grouped[HIDDEN_ALBUM].append(file_id)
    summary = {"favourites": 0, "albums": 0, "dates": 0}
    if dated:
        with lib.transaction() as db:
            before = db.total_changes
            # New copies take the Photos date; photos already in the library only replace a weak guess.
            db.executemany("UPDATE files SET taken_at=?, date_source='iphone' WHERE id=? AND "
                           "COALESCE(date_source,'') != 'manual' AND (? OR COALESCE(date_source,'modified') "
                           "IN ('modified','filename','inferred'))", dated)
            summary["dates"] = db.total_changes - before
    if favourites:
        summary["favourites"] = organisation.edit(lib, favourites, favorite=True)
    existing = {r["name"].casefold(): r["id"] for r in lib.db.execute(
        "SELECT id, name FROM albums WHERE kind='manual' AND rule_json IS NULL ORDER BY id DESC")}
    for name, ids in grouped.items():
        if name.casefold() in existing:
            album_engine.add(lib, existing[name.casefold()], ids)
        else:
            existing[name.casefold()] = album_engine.create(lib, name, ids)
        summary["albums"] += 1
    return summary
