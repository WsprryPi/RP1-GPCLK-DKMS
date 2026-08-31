#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify repository-relative Markdown links without network access."""

from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
pattern = re.compile(r"\[[^]]*\]\(([^)]+)\)")
failures = []
for document in [*ROOT.glob("*.md"), *(ROOT / "docs").rglob("*.md")]:
    for target in pattern.findall(document.read_text(encoding="utf-8")):
        target = target.split("#", 1)[0]
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        resolved = (document.parent / unquote(target)).resolve()
        if not resolved.exists():
            failures.append(f"{document.relative_to(ROOT)} -> {target}")
if failures:
    raise SystemExit("broken documentation links:\n" + "\n".join(failures))
print("documentation links: PASS")
