#!/usr/bin/env python3
"""Inject the student-tools toolbar (scripts/student_tools.py) into every SAT
study page (HTML files paired with a .md source). Idempotent: pages already
carrying the marker are skipped.

Usage:
    python scripts/add_student_tools.py          # inject
    python scripts/add_student_tools.py --check  # verify only
"""

import sys
from pathlib import Path

# Ensure UTF-8 stdout on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from student_tools import MARKER, inject  # noqa: E402


def targets():
    sat = WORKSPACE_ROOT / "SAT"
    out = []
    for html in sorted(sat.rglob("*.html")):
        if html.name in ("index.html", "README.html"):
            continue
        if "Skills" in html.parts or "Show" in html.parts or "Test" in html.parts:
            continue  # already interactive drills / toy mocks
        if "webapp" in html.parts:
            continue  # standalone app
        if not html.with_suffix(".md").exists():
            continue  # only .md-paired study pages
        out.append(html)
    return out


def main():
    check_only = "--check" in sys.argv
    files = targets()
    print(f"Student-tools target pages: {len(files)}")
    changed, skipped = 0, 0
    for html in files:
        text = html.read_text(encoding="utf-8")
        if MARKER in text:
            skipped += 1
            continue
        if check_only:
            print(f"  MISSING: {html.relative_to(WORKSPACE_ROOT).as_posix()}")
            continue
        new_text, did = inject(text)
        if did:
            html.write_text(new_text, encoding="utf-8")
            changed += 1
            print(f"  [INJECTED] {html.relative_to(WORKSPACE_ROOT).as_posix()}")
    print(f"Done. injected={changed} already_present={skipped}")
    if check_only:
        sys.exit(0)


if __name__ == "__main__":
    main()
