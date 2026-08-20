#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the final staging/same-version non-authorizing decision prompt."""
from __future__ import annotations
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
text = (ROOT / "docs/contracts/phase5.53-final-staging-same-version-authorization-decision-prompt.md").read_text()
for required in (
    "c0bfeb18f12f5eed63f0a00319ca446864056fdd",
    "f8ea112c2b3ff1fe18c8d48dc54f4ee8a5f41427595a163ddde2907e11c9a73b",
    "30f93036c63db3c2ca9a6d14c9905928f940878c12d5d757c0d761ad4eedbb3c",
    "c32b3f196b48aa0c10da4067173d6025f91c642f7ff3b5c770d5ef5fba5d0bf2",
    "exactly one ledger-bound inactive product removal",
    "authenticated qualification installation with sealed recovery",
    "Stop before lifecycle attempt 1",
    "executionReady=false",
    "do not contact `wspr5`",
):
    assert required in text
assert text.count("## Exact authorization phrase") == 1
assert "This prompt is non-authorizing" in text
assert "I do not authorize any Gate D attempt" in text
assert "**Superseded:**" in text and "must not be reused" in text
print("Phase 5.53 final staging and same-version authorization decision: PASS")
