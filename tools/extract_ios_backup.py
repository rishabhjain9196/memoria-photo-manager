#!/usr/bin/env python3
"""Copy files out of an iPhone/iPad backup into readable folders (command-line front end).

Uses the same engine as Memoria's "Import from iPhone backup": the backup is opened read-only, copies
keep each file's original date, existing files are never overwritten, and an interrupted run resumes
where it stopped (press Ctrl+C to stop safely).

Examples:
  python tools/extract_ios_backup.py --list
  python tools/extract_ios_backup.py "D:\\iPhone export" --what photos
  python tools/extract_ios_backup.py "D:\\iPhone export" --backup "<backup folder>" --what all --dry-run
  python tools/extract_ios_backup.py "D:\\Pictures" --library --what photos   # only photos not already in the library
"""
from __future__ import annotations

import argparse
import os
import signal
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memoria.engine import iosbackup  # noqa: E402
from memoria.engine.progress import Cancelled, Progress  # noqa: E402

PRESETS = {
    "photos": list(iosbackup.MEDIA_CATEGORIES),
    "whatsapp": ["whatsapp_media", "whatsapp_data"],
    "apps": ["app_documents", "apps", "whatsapp_data"],
    "system": ["system"],
    "all": list(iosbackup.CATEGORIES),
}


def _size(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _categories(spec: str) -> list[str]:
    out: list[str] = []
    for part in spec.split(","):
        part = part.strip().lower()
        out += PRESETS.get(part, [part])
    unknown = [c for c in out if c not in iosbackup.CATEGORIES]
    if unknown:
        raise SystemExit(f"Unknown --what value(s): {', '.join(unknown)}. Use "
                         f"{', '.join(PRESETS)} or: {', '.join(iosbackup.CATEGORIES)}")
    return list(dict.fromkeys(out))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("destination", nargs="?", help="Output folder (or the library folder with --library)")
    ap.add_argument("--backup", help="Backup folder (default: the newest backup found on this PC)")
    ap.add_argument("--list", action="store_true", help="List backups found on this PC and exit")
    ap.add_argument("--what", default="photos", help="photos, whatsapp, apps, system, all, or category keys (comma list)")
    ap.add_argument("--library", action="store_true",
                    help="DESTINATION is a Memoria library: import only photos/videos it doesn't already hold")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be copied, copy nothing")
    args = ap.parse_args()

    if args.list:
        backups = iosbackup.find_backups()
        if not backups:
            print("No backups found in:", *map(str, iosbackup.default_backup_dirs()), sep="\n  ")
        for b in backups:
            flags = (" [encrypted]" if b.encrypted else "") + (" [incomplete]" if b.complete is False else "")
            print(f"{b.label}{flags}\n  {b.path}")
        return 0
    if not args.destination:
        ap.error("destination is required (or use --list)")

    if args.backup:
        backup = iosbackup.read_backup(args.backup)
    else:
        found = iosbackup.find_backups()
        if not found:
            raise SystemExit("No backups found on this PC. Pass --backup <folder>.")
        backup = found[0]
    print(f"Backup:  {backup.label}\n         {backup.path}")
    if backup.complete is False:
        print("Warning: this backup did not finish; some files may be missing.")
    categories = list(iosbackup.MEDIA_CATEGORIES) if args.library else _categories(args.what)
    entries = iosbackup.list_files(backup)
    summary = iosbackup.summarize(entries, media_only=args.library)
    for key in categories:
        files, size = summary[key]
        print(f"  {iosbackup.CATEGORIES[key][0]:<34} {files:>8,} files  {_size(size):>10}")
    if args.dry_run:
        return 0

    lib = None
    if args.library:
        from memoria.engine.db import Library
        lib = Library(args.destination)
        dest = iosbackup.default_library_folder(lib, backup)
    else:
        dest = args.destination
    print(f"Copying to {dest}  (Ctrl+C stops safely; run again to resume)")

    cancel = threading.Event()
    signal.signal(signal.SIGINT, lambda *_: cancel.set())
    started = time.monotonic()
    last = {"detail": {}}

    def show(done, total, message):
        items = last["detail"].get("items")
        copied = last["detail"].get("bytes")
        speed = copied[0] / max(0.001, time.monotonic() - started) if copied else 0
        line = f"\r{message[:70]:<70}"
        if items and copied:
            line = (f"\r{items[0]:,}/{items[1]:,} files · {_size(copied[0])} of {_size(copied[1])} · "
                    f"{_size(speed)}/s   ")
        sys.stdout.write(line)
        sys.stdout.flush()

    progress = Progress(show, cancel, interval=0.5, detail_callback=lambda d: last.update(detail=d))
    try:
        result = iosbackup.extract(backup, dest, categories, progress=progress, media_only=args.library,
                                   library=lib, entries=entries)
    except Cancelled:
        print("\nStopped safely. Run the same command again to resume.")
        return 130
    finally:
        if lib is not None:
            lib.close()
    print(f"\nCopied {result.copied:,} files ({_size(result.copied_bytes)}); "
          f"{result.resumed:,} already done; {result.already_in_library:,} already in the library; "
          f"{result.renamed:,} renamed to avoid clashes; {result.missing:,} missing; {result.failed:,} failed.")
    for line in result.errors[:20]:
        print("  ", line)
    if lib is not None:
        print("Open the library in Memoria and rescan (F5) to add the new files.")
    return 0 if not result.failed else 1


if __name__ == "__main__":
    sys.exit(main())
