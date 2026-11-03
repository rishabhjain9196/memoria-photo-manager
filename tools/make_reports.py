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
    "test_photoedit": "Photo editor",
    "test_videoedit": "Video editor",
    "test_video": "Video compressor",
    "test_story": "Story maker",
    "test_ui_smoke": "Desktop UI — end to end",
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
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    if os.name == "nt":
        env.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"))
    print("Running tests…")
    t0 = datetime.now()
    subprocess.run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={xml_path}"],
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
    for p in (ROOT / "test-library" / "expected.json",):
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    sys.path.insert(0, str(ROOT))
    from memoria.samplelib import build
    with tempfile.TemporaryDirectory() as d:
        return build(Path(d) / "lib", small=False, videos=True)


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
        style = f' style="color:{color}"' if color else ""
        return f'<div class="card"><p>{e(label)}</p><h4 style="font-size:26px;margin:4px 0 0"{style}>{e(str(value))}</h4></div>'

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
        parts.append("<p>Benchmark not run for this report (<code>--no-bench</code>).</p>")
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
        parts.append("<p>The full test library (<code>tools/make_test_library.py</code>) contains these known cases; "
                     "the test suite uses a smaller variant with the same scenarios.</p><table><tr><th>Scenario</th><th>Count</th></tr>")
        parts += [f"<tr><td>{k}</td><td class='num'>{v}</td></tr>" for k, v in rows]
        parts.append("</table>")
    parts.append("</section><section id='env'><h2>Environment</h2><table><tr><th>Component</th><th>Version</th></tr>")
    parts += [f"<tr><td>{e(k)}</td><td>{e(v)}</td></tr>" for k, v in versions()]
    parts.append("""</table></section><section id="repro"><h2>Reproduce</h2>
<pre><code>.\\.venv\\Scripts\\python -m pytest -q
.\\.venv\\Scripts\\python tools\\benchmark.py --photos 500
.\\.venv\\Scripts\\python tools\\make_reports.py        # regenerates this page</code></pre></section>
<footer>Memoria quality report · <a href="index.html">Documentation home</a></footer></main></div></body></html>""")
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--photos", type=int, default=500)
    ap.add_argument("--no-bench", action="store_true")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        tests = run_tests(tmp)
        bench = None if a.no_bench else run_bench(tmp, a.photos)
    page = render(tests, bench, ground_truth())
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT}")
    failed = sum(c["status"] in ("failed", "error") for c in tests["cases"])
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
