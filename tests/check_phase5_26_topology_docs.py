#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the packaged Phase 5.26 Si5351/GPIO topology correction."""
from __future__ import annotations
import json, pathlib, subprocess

ROOT=pathlib.Path(__file__).resolve().parents[1]
paths=[ROOT/"docs/operator/gate-d-target-runbook.md",
       ROOT/"docs/contracts/gate-d-target-authorization-dossier.md"]
for path in paths:
 text=path.read_text()
 normalized=" ".join(text.split()).lower()
 assert "separate I2C-controlled Si5351 output path" in text
 assert "si5351 is not wired to either pin" in normalized
 assert "si5351Disconnected" in text
 assert "disconnected from GPIO4 and GPIO20" not in text
 assert "Si5351 leads must remain disconnected" not in text

layout=json.loads((ROOT/"release/release-layout-v1.json").read_text())
assert layout["release"]=="0.0.0-phase5.48"
tracked=set(subprocess.check_output(["git","ls-files"],cwd=ROOT,text=True).splitlines())
assert "docs/operator/gate-d-target-runbook.md" in tracked
assert "docs/contracts/gate-d-target-authorization-dossier.md" in tracked
print("Phase 5.26 packaged topology documentation: PASS")
