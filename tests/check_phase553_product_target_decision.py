#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path

p = (Path(__file__).resolve().parents[1] / "docs/contracts/phase5.53-product-only-target-reset-install-authorization-prompt.md").read_text()
for required in (
    "4e7a64a0ca353d2fcab6e25891f5254746e2b91a",
    "0261c25f785458a0ee3cd270e4a7afcb606f5a86fdb99fc019aae231388c78f1",
    "032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76",
    "qualification archive is explicitly excluded",
    "remove --execute",
    "install --execute --allow-development --route gpio4",
    "Until that exact phrase is supplied, do not contact or mutate the target",
):
    assert required in p
print("Phase 5.53 product-only target decision: PASS")
