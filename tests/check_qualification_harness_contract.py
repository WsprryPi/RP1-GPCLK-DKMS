#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the maintained external Harness integration boundaries."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = (ROOT / "docs/contracts/qualification-harness-integration.md").read_text()

for mode in ("WSPR", "Tone", "QRSS", "FSKCW", "DFCW"):
    assert mode in contract
for label in ("externally consumable", "hardware-free exercised",
              "live-plan ready", "not ready", "not applicable"):
    assert label in contract
for state in ("requested", "persisted", "configured", "active-overlay",
              "module-reported", "reconciled", "live-eligible"):
    assert state in contract
for boundary in ("fixture blockage", "semantic validator", "exactly one",
                 "immutable", "terminal-silence", "REQUIRED-BEFORE-LIVE"):
    assert boundary in contract
for route_id in (
    "v0.9.0-pi5-gpio4",
    "v0.9.0-pi5-gpio20",
):
    assert route_id in (ROOT / "docs/contracts/development-identity.md").read_text()
for prohibited in ("/dev/mem", "automatic fallback", "continuous TONE"):
    assert prohibited in contract

assert "does not authorize target execution" in contract
assert "The template is not authorization" in contract
required_campaign = "finite carrier, WSPR, QRSS, FSKCW, and DFCW"
assert required_campaign in contract
assert "QRSS, FSKCW, and DFCW are the three required QRSS-family modes" in contract
assert "one keyed-mode result does not satisfy another" in contract
print("Qualification Harness integration contract: PASS")
