#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Prove the final product has the exact representative-build closure."""
import json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
OLD="1884c0f1c53c661495576bf10ce08d8bf7a90bc3";NEW="4e7a64a0ca353d2fcab6e25891f5254746e2b91a"
paths=("Kbuild","Makefile","dkms.conf","include","src")
changed=subprocess.check_output(["git","diff","--name-only",OLD,NEW,"--",*paths],cwd=ROOT,text=True).strip()
assert changed==""
evidence=json.loads((ROOT/"docs/evidence/phase5.53-representative-build-transfer.json").read_text())
manifest=json.loads((ROOT/evidence["representativeBuildManifest"]).read_text())
assert manifest["result"]["moduleSha256"]==evidence["representativeModuleSha256"]
assert evidence["gitDiffEmpty"] is True and evidence["finalArchiveMembersMatchFinalCommit"] is True
print("Phase 5.53 representative build transfer: PASS")
