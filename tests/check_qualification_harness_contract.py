#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the external Harness and Step 4 handoff boundaries."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = (ROOT / "docs/contracts/qualification-harness-integration.md").read_text()
handoff = (ROOT / "docs/contracts/roadmap-step4-wsprrypi-handoff.md").read_text()

for mode in ("WSPR", "Tone", "QRSS", "FSKCW", "DFCW"):
    assert mode in contract and mode in handoff
for label in ("externally consumable", "hardware-free exercised",
              "live-plan ready", "not ready", "not applicable"):
    assert label in contract
for state in ("requested", "persisted", "configured", "active-overlay",
              "module-reported", "reconciled", "live-eligible"):
    assert state in contract and state in handoff
for boundary in ("fixture blockage", "semantic validator", "exactly one",
                 "immutable", "terminal-silence", "REQUIRED-BEFORE-LIVE"):
    assert boundary in contract
for route_id in (
    "v0.9.0-pi5-gpio4-6.18.34-development",
    "v0.9.0-pi5-gpio20-6.18.34-development",
):
    assert route_id in (ROOT / "docs/contracts/development-identity.md").read_text()
for prohibited in ("/dev/mem", "automatic fallback", "continuous TONE"):
    assert prohibited in handoff or prohibited in contract

assert "does not authorize Step 5" in handoff
assert "The template is not authorization" in contract
required_campaign = "finite carrier, WSPR, QRSS, FSKCW, and DFCW"
assert required_campaign in handoff
assert "QRSS, FSKCW, and DFCW are the three required QRSS-family modes" in contract
assert "one keyed-mode result does not satisfy another" in contract
print("Qualification Harness integration contract: PASS")
