#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check the repository's per-file SPDX policy for governed source files."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    ".c": {"MIT", "GPL-2.0-only OR MIT"},
    ".h": {"GPL-2.0-only OR MIT", "(GPL-2.0-only WITH Linux-syscall-note) OR MIT"},
    ".md": {"MIT"},
    ".json": {"MIT"},
    ".py": {"MIT"},
    ".sh": {"MIT"},
}
SCAN = ["docs", "include", "schema", "src", "tests"]


def identifier(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines()[:5]:
        marker = "SPDX-License-Identifier:"
        if '"SPDX-License-Identifier": "MIT"' in line:
            return "MIT"
        if marker in line:
            value = line.split(marker, 1)[1].strip().rstrip(" -->*/,")
            return value.strip('"')
    return None


failures = []
for directory in SCAN:
    for path in (ROOT / directory).rglob("*"):
        if not path.is_file() or path.suffix not in EXPECTED:
            continue
        found = identifier(path)
        allowed = set(EXPECTED[path.suffix])
        if path.is_relative_to(ROOT / "tests"):
            allowed.add("MIT")
        if found not in allowed:
            failures.append(f"{path.relative_to(ROOT)}: unexpected SPDX {found!r}")

if failures:
    print("\n".join(failures), file=sys.stderr)
    raise SystemExit(1)
print("SPDX policy: PASS")
