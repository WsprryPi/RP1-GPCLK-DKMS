#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path

p = (Path(__file__).resolve().parents[1] / "docs/contracts/phase5.53-product-only-target-reset-install-authorization-prompt.md").read_text()
for required in (
    "40b2ffd2fa944511b549737bcf6eb1a199125971",
    "0261c25f785458a0ee3cd270e4a7afcb606f5a86fdb99fc019aae231388c78f1",
    "c46cec7641fc7e0aae31a86ce2e9ec78948deb8f22fe55cdfdde34636b2e4d3b",
    "qualification archive is explicitly excluded",
    "remove --execute",
    "install --execute --allow-development --route gpio4",
    "Until that exact phrase is supplied, do not contact or mutate the target",
):
    assert required in p
print("Phase 5.53 product-only target decision: PASS")
