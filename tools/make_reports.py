"""Run the test suite and benchmark, then write docs/report.html.

    python tools/make_reports.py                 # tests + benchmark (500 photos)
    python tools/make_reports.py --photos 1000   # bigger benchmark
    python tools/make_reports.py --no-bench      # tests only

Only non-identifying environment details are recorded (no host or user names, no paths).
"""
from __future__ import annotations

import argparse
import ast
import html
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
OUT = ROOT / "docs" / "report.html"

AREAS = {
    "test_engine": "Engine — ground truth, safety and undo",
    "test_safety": "Catalogue integrity — drives, locks, schema, long paths",
    "test_batch": "Batch actions and Check everything",
    "test_videosim": "Similar videos",
    "test_dupfolders": "Duplicate folders",
    "test_duplicate_choices": "Explicit duplicate choices, remembered keeps and all-copy removal safety",
    "test_faces": "People (face recognition)",
    "test_albums": "Albums and places",
    "test_photoedit": "Photo editor",
    "test_videoedit": "Video editor",
    "test_video": "Video compressor",
    "test_story": "Story maker",
    "test_ui_smoke": "Desktop UI — end to end",
    "test_storage": "Selective reset, interruption recovery and storage",
    "test_insights": "Storage charts, timeline, offline map and filtered browsing",
    "test_metadata": "Extended photo/video metadata, migration, filters and numeric sorting",
    "test_diagnostics": "Aggregate diagnostic privacy, cached reports, opt-in and publication",
    "test_live_index": "Live browsing during indexing and utility safety",
    "test_notifications": "Key-event notification routing, privacy, preferences and shutdown",
    "test_library_roots": "Multi-folder identities, offline retention, migration and reconnect-safe Undo",
    "test_library_views": "Bounded History, Health and Compare views and folder management",
    "test_assets": "Linked-component discovery and mandatory review",
    "test_companion_actions": "Compound file operations, rollback, cancellation and recovery",
    "test_metadata_history": "Duplicate organisation merge, conflict-aware Undo and reset safety",
    "test_organisation": "Tags, ratings, favourites and Pick/Reject states",
    "test_smart_albums": "Dynamic saved rules and bounded album browsing",
    "test_responsive_views": "100k-entry responsiveness, asynchronous previews and lifecycle guards",
    "test_duplicate_paging": "Bounded duplicate-group and member review",
    "test_duplicate_cleanup": "Exact folder collections and verified keep-one cleanup",
    "test_duplicate_bulk_ui": "Scoped folder/all-group cleanup confirmation and Undo",
    "test_media_source_ui": "Guarded asynchronous editor, story and video sources",
    "test_folder_comparison": "Shared-only subset review, unique content and Undo",
    "test_recovery_accounting": "Read-only cumulative Recovery accounting and inspection",
    "test_recovery_restore": "Reviewed logged/unlogged Recovery restoration and conflict safety",
    "test_recovery_restore_ui": "Restoration preview, scoped conflict popups and bounded UI",
}


def docstrings(test_file: Path) -> dict[str, str]:
    out = {}
    tree = ast.parse(test_file.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            doc = ast.get_docstring(node)
            if doc:
                out[node.name] = doc.strip().splitlines()[0]
    return out


def pretty(name: str) -> str:
    name = re.sub(r"\[.*\]$", "", name)[5:].replace("_", " ")
    return name[:1].upper() + name[1:]


def run_tests(tmp: Path) -> dict:
    xml_path = tmp / "junit.xml"
    env = dict(os.environ, PYTHONIOENCODING="utf-8", MEMORIA_SHOT_LABEL="<b>Sample library</b><br>Generated test media")
    if os.name == "nt":
        env.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"))
    print("Running tests…")
    t0 = datetime.now()
    subprocess.run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={xml_path}",
                    f"--basetemp={tmp / 'pytest'}"],
                   cwd=ROOT, env=env)
    wall = (datetime.now() - t0).total_seconds()
    root = ET.parse(xml_path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    docs = {}
    for f in (ROOT / "tests").glob("test_*.py"):
        docs[f.stem] = docstrings(f)
    cases = []
    for c in suite.iter("testcase"):
        module = c.get("classname", "").split(".")[-1]
        status = "passed"
        msg = ""
        for tag in ("failure", "error", "skipped"):
            el = c.find(tag)
            if el is not None:
                status = {"failure": "failed", "error": "error", "skipped": "skipped"}[tag]
                msg = (el.get("message") or "")[:300]
        name = c.get("name")
        cases.append({"module": module, "name": name, "title": docs.get(module, {}).get(re.sub(r"\[.*\]$", "", name))
                      or pretty(name), "time": float(c.get("time", 0)), "status": status, "message": msg})
    return {"cases": cases, "wall": wall}


def run_bench(tmp: Path, photos: int) -> dict | None:
    print(f"Running benchmark with {photos} photos…")
    out = tmp / "bench.json"
    r = subprocess.run([PY, str(ROOT / "tools" / "benchmark.py"), str(tmp / "bench"), "--photos", str(photos),
                        "--json", str(out)], cwd=ROOT, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    return json.loads(out.read_text(encoding="utf-8")) if r.returncode == 0 and out.exists() else None


def ground_truth() -> dict | None:
    sys.path.insert(0, str(ROOT))
    from memoria.samplelib import build
    with tempfile.TemporaryDirectory() as d:
        return build(Path(d) / "lib", small=True, videos=True)


def versions() -> list[tuple[str, str]]:
    from importlib.metadata import PackageNotFoundError, version
    rows = [("Python", platform.python_version()), ("OS", f"{platform.system()} {platform.release()}"),
            ("CPU threads", str(os.cpu_count()))]
    for pkg in ("PySide6", "numpy", "Pillow", "pillow-heif", "xxhash", "imageio-ffmpeg", "opencv-python-headless", "pytest"):
        try:
            rows.append((pkg, version(pkg)))
        except PackageNotFoundError:
            pass
    return rows


def refresh_images(tmp: Path) -> None:
    """Publish screenshots made by the passing end-to-end test, never a user's library."""
    overview = next(tmp.rglob("01-overview.png"))
    shots = overview.parent
    names = {
        "welcome": "00-welcome", "overview": "01-overview", "photos": "02-photos",
        "viewer": "photos-viewer", "duplicates": "03-duplicates", "duplicates-folders": "03-duplicates-folders",
        "similar": "04-similar", "similar-videos": "04-similar-videos", "blurry": "04-similar-blurry",
        "tidy": "05-tidy", "organize": "06-organize", "editor-crop": "07-editor-crop",
        "editor-video": "07-editor-video", "story": "08-story", "video": "09-video", "health": "10-health",
        "compare": "11-compare", "history": "12-history", "people": "13-people",
        "people-lookalike": "13-people-lookalike", "albums": "14-albums", "albums-make": "14-albums-make",
        "toast": "20-after-apply-toast",
    }
    for name in ("dark-overview", "dark-photos", "dark-similar", "insights-storage", "insights-timeline",
                 "insights-india", "insights-world", "insights-files", "dark-insights", "photos-largest", "library-filters",
                 "storage-reset", "storage-reset-hard"):
        names[name] = name
    for name in ("library-filters-video", "library-filters-camera", "photos-video-metadata"):
        names[name] = name
    sources = {dest: shots / f"{source}.png" for dest, source in names.items()}
    sources["confirm"] = next(shots.glob("dialog-Move*.png"))
    sources["live-index"] = next(tmp.rglob("live-index.png"))
    sources["history"] = shots / "21-history-after-apply.png"
    for dest, source in (("duplicates-choices", "duplicates-file-choices"),
                         ("duplicates-remove-all-confirm", "duplicates-remove-all-confirm"),
                         ("duplicates-quick-mode", "duplicates-quick-mode"),
                         ("duplicates-subset", "duplicates-subset"),
                         ("duplicates-many", "duplicates-many"),
                         ("duplicates-folder-grouping", "duplicates-folder-grouping"),
                         ("duplicates-clean-all-confirm", "duplicates-clean-all-confirm"),
                         ("recovery-restore-preview", "recovery-restore-preview"),
                         ("recovery-restore-conflict", "recovery-restore-conflict"),
                         ("tidy-sidecars", "tidy-sidecars")):
        sources[dest] = next(tmp.rglob(f"{source}.png"))
    for path in sources.values():
        if not path.is_file():
            raise FileNotFoundError(f"Expected documentation screenshot was not generated: {path.name}")
    for dest, path in sources.items():
        shutil.copyfile(path, ROOT / "docs" / "images" / f"{dest}.png")


def render(tests: dict, bench: dict | None, gt: dict | None) -> str:
    e = html.escape
    cases = tests["cases"]
    counts = defaultdict(int)
    for c in cases:
        counts[c["status"]] += 1
    total_time = sum(c["time"] for c in cases)
    ok = counts["failed"] == 0 and counts["error"] == 0
    by_mod = defaultdict(list)
    for c in cases:
        by_mod[c["module"]].append(c)

    def tile(value, label, color=""):
        style = "font-size:26px;margin:4px 0 0" + (f";color:{color}" if color else "")
        return f'<div class="card"><p>{e(label)}</p><h4 style="{style}">{e(str(value))}</h4></div>'

    parts = [f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Memoria — Quality report</title><link rel="stylesheet" href="style.css">
<link rel="icon" href="../memoria/ui/assets/memoria.png">
<style>.st{{font-weight:600}} .st.passed{{color:var(--ok)}} .st.failed,.st.error{{color:var(--danger)}} .st.skipped{{color:var(--warn)}}
td.num{{text-align:right;white-space:nowrap}} details summary{{cursor:pointer;font-weight:600;margin:10px 0}}</style></head><body>
<div class="top"><div class="inner"><a class="brand" href="index.html"><img src="../memoria/ui/assets/memoria.png" alt="">Memoria</a>
<nav><a href="design.html">Design</a><a href="features.html">Features</a><a href="technical.html">Technical</a><a class="active" href="report.html">Quality report</a></nav></div></div>
<div class="layout"><aside class="toc"><b>QUALITY REPORT</b><a href="#summary">Summary</a><a href="#tests">Test results</a>
{''.join(f'<a class="sub" href="#{m}">{e(AREAS.get(m, m))}</a>' for m in by_mod)}
<a href="#bench">Benchmark</a><a href="#truth">Test library ground truth</a><a href="#env">Environment</a><a href="#repro">Reproduce</a></aside><main>
<header class="hero"><h1>Quality report</h1><p>Automated test results and performance measurements for Memoria.</p>
<div class="meta"><span class="pill">Generated {datetime.now():%d %b %Y, %H:%M}</span><span class="pill">by tools/make_reports.py</span></div></header>
<section id="summary"><h2>Summary</h2>
<div class="callout {'ok' if ok else 'danger'}"><b>{'All tests passed.' if ok else 'Some tests failed.'}</b>
{counts['passed']} passed, {counts['failed'] + counts['error']} failed, {counts['skipped']} skipped in {tests['wall']:.0f} s.</div>
<div class="grid">{tile(len(cases), 'Tests')}{tile(counts['passed'], 'Passed', 'var(--ok)')}
{tile(counts['failed'] + counts['error'], 'Failed', 'var(--danger)' if not ok else '')}{tile(f"{total_time:.0f} s", 'Time in tests')}</div>
<table><tr><th>Area</th><th>Tests</th><th>Passed</th><th>Time</th></tr>"""]
    for m, cs in by_mod.items():
        parts.append(f"<tr><td><a href='#{m}'>{e(AREAS.get(m, m))}</a></td><td class='num'>{len(cs)}</td>"
                     f"<td class='num'>{sum(c['status'] == 'passed' for c in cs)}</td>"
                     f"<td class='num'>{sum(c['time'] for c in cs):.1f} s</td></tr>")
    parts.append("</table></section><section id='tests'><h2>Test results</h2>"
                 "<p>Every test name below states the behaviour it proves. Engine tests run against a generated library "
                 "whose expected results are recorded in <code>expected.json</code>.</p>")
    for m, cs in by_mod.items():
        parts.append(f"<h3 id='{m}'>{e(AREAS.get(m, m))} <span class='pill'>tests/{m}.py</span></h3>"
                     "<table><tr><th>Behaviour verified</th><th>Result</th><th>Time</th></tr>")
        for c in cs:
            msg = f"<br><small style='color:var(--danger)'>{e(c['message'])}</small>" if c["message"] else ""
            parts.append(f"<tr><td>{e(c['title'])}<br><small style='color:var(--muted)'><code>{e(c['name'])}</code></small>{msg}</td>"
                         f"<td class='st {c['status']}'>{c['status'].capitalize()}</td><td class='num'>{c['time']:.2f} s</td></tr>")
        parts.append("</table>")
    parts.append("</section><section id='bench'><h2>Benchmark</h2>")
    if bench:
        parts.append(f"<p>{bench['files']:,} generated 6 MP JPEGs (5% exact copies), {bench['bytes'] / 1e9:.2f} GB, on "
                     f"{bench['cpu_count']} CPU threads. Absolute numbers depend on the machine and disk.</p>"
                     "<table><tr><th>Stage</th><th>Time</th><th>Result</th></tr>")
        for s in bench["stages"]:
            parts.append(f"<tr><td>{e(s['stage'])}</td><td class='num'>{s['seconds']:.2f} s</td><td>{e(s['note'])}</td></tr>")
        parts.append("</table>")
    else:
        parts.append("<p>Benchmark not run for this report (<code>--no-bench</code>) to avoid generating a large "
                     "media copy. Tests exercise 10,000 synthetic catalogue entries representing 300 GB, bounded "
                     "paging/queues, dense similarity, crash recovery and interactive UI flows. This is not a "
                     "measurement of real 200–300 GB library throughput.</p>")
    parts.append("</section><section id='truth'><h2>Test library ground truth</h2>")
    if gt:
        rows = [("Total files", gt["total_files"]), ("Total size", f"{gt['total_bytes'] / 1e6:.1f} MB"),
                ("Exact-duplicate groups", len(gt["duplicate_groups"])),
                ("…of which large (&gt; 1.28 MB) originals", len(gt["large_duplicates"])),
                ("Bursts (5 frames, known best)", len(gt["bursts"])), ("Near-duplicates (WhatsApp-style)", len(gt["near_duplicates"])),
                ("Blurry photos", len(gt["blurry"])), ("Junk files", len(gt["junk"])), ("Empty files", len(gt["empty_files"])),
                ("Empty folders", len(gt["empty_folders"])), ("Corrupt photos", len(gt["corrupt"])),
                ("Non-media files", len(gt["non_media"])), ("EXIF-rotated photos", len(gt["rotated"])),
                ("Files with a known date and source", len(gt["dates"])), ("Files with no reliable date", len(gt["uncertain_dates"])),
                ("Videos", len(gt["videos"])), ("HEIC photos", len(gt["heic"]))]
        parts.append("<p>The small generated library used by the tests and documentation screenshots contains "
                     "these known cases. <code>tools/make_test_library.py</code> can also generate a larger variant."
                     "</p><table><tr><th>Scenario</th><th>Count</th></tr>")
        parts += [f"<tr><td>{k}</td><td class='num'>{v}</td></tr>" for k, v in rows]
        parts.append("</table>")
    parts.append("</section><section id='env'><h2>Environment</h2><table><tr><th>Component</th><th>Version</th></tr>")
    parts += [f"<tr><td>{e(k)}</td><td>{e(v)}</td></tr>" for k, v in versions()]
    parts.append("""</table></section><section id="repro"><h2>Reproduce</h2>
<pre><code>.\\.venv\\Scripts\\python -m pytest -q
.\\.venv\\Scripts\\python tools\\benchmark.py --photos 500
.\\.venv\\Scripts\\python tools\\make_reports.py --no-bench --refresh-images
# Regenerates this report and documentation images using disposable test media.</code></pre></section>
<footer>Memoria quality report · <a href="index.html">Documentation home</a></footer></main></div></body></html>""")
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--photos", type=int, default=500)
    ap.add_argument("--no-bench", action="store_true")
    ap.add_argument("--refresh-images", action="store_true", help="refresh docs images from the passing UI test")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        tests = run_tests(tmp)
        bench = None if a.no_bench else run_bench(tmp, a.photos)
        if a.refresh_images and all(c["status"] == "passed" for c in tests["cases"]):
            refresh_images(tmp)
    page = render(tests, bench, ground_truth())
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT}")
    failed = sum(c["status"] in ("failed", "error") for c in tests["cases"])
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
