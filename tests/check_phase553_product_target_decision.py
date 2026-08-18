#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path

p = (Path(__file__).resolve().parents[1] / "docs/contracts/phase5.53-product-only-target-reset-install-authorization-prompt.md").read_text()
for required in (
    "f293955585d3b95efd893dec2c1d376fde4fc7ea",
    "83b1de0e82c30ab4c2781dc941eef0556d6bfede",
    "d014e60f7a76d6c5b178ff5bec4caa1d4978f4a9fd0a2a6a5552614c7d6b2276",
    "qualification archive is explicitly excluded",
    "remove --execute",
    "install --execute --allow-development --route gpio4",
    "Until that exact phrase is supplied, do not contact or mutate the target",
):
    assert required in p
print("Phase 5.53 product-only target decision: PASS")
