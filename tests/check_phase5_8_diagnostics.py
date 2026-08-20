#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Deterministic offline checks for the Phase 5.8 diagnostics contract."""

from __future__ import annotations
import importlib.util, json, pathlib, tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("diagnostics",ROOT/"scripts/rp1-gpclk-diagnostics.py")
module=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(module)
contract=json.loads((ROOT/"release/diagnostics-contract-v1.json").read_text())
assert contract["readOnly"] is True and len(contract["categories"])==6
assert {"module-load","overlay-apply","gpio-write","repair","rf"} <= set(contract["prohibitedActions"])

def write(root: pathlib.Path, name: str, value):
    path=root/name.lstrip("/"); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value) if isinstance(value,(dict,list)) else value)

commands=[]
def runner(args):
    commands.append(args)
    assert args[0] in {"dpkg-query","dkms","modinfo","journalctl"}
    if args[0]=="journalctl": assert args[1:5]==["-k","-b","--no-pager","-g"]
    return {"status":"ok","exitStatus":0,"stdout":"fixture\n","stderr":"","truncated":False}

with tempfile.TemporaryDirectory() as temporary:
    root=pathlib.Path(temporary); kernel="6.18.34+rpt-rpi-2712"
    (root/f"lib/modules/{kernel}/build").mkdir(parents=True)
    write(root,f"/lib/modules/{kernel}/updates/dkms/{module.MODULE}.ko","module")
    write(root,"/proc/device-tree/model","Raspberry Pi 5 Model B")
    write(root,"/sys/module/rp1_gpclk_dkms/parameters/live_output","0")
    write(root,"/var/lib/rp1-gpclk-dkms/transaction.json",{"status":"complete","ownedFiles":[],"ownedDirectories":[]})
    query={"status":"ok","abiMin":1,"abiMax":1,"route":"GPIO4","compatibilityState":"Compatible-unqualified",
           "compatibilityReason":"identity-unknown","compatibilityId":"entry","capabilities":["route-identity"],"cleanupFault":False}
    write(root,"/run/rp1-gpclk-dkms/query-fixture.json",query)
    release=root/"release"; release.mkdir()
    write(root,"/release/rp1-gpclk-compatibility-manifest.json",{"manifestId":"manifest","entries":[{"id":"entry","route":"GPIO4","state":"Compatible-unqualified","liveEligible":False,"reason":"build only"}]})
    write(root,"/release/release-metadata.json",{"release":module.VERSION})
    write(root,"/release/SHA256SUMS","0"*64+"  fixture\n")
    report=module.Collector(root,runner,kernel,"aarch64").collect(release)
    assert report["readOnly"] is True
    assert report["summary"]["category"]=="build-compatible-but-live-disabled"
    assert report["compatibility"]["selectedEntry"]=="entry"
    assert report["module"]["file"]["sha256"]
    assert report["module"]["signatureStatus"]["status"]=="signed"
    assert report["module"]["liveGate"]["value"]=="0"
    assert report["kernels"]["headers"][kernel]["present"] is True
    assert report["endpoint"]["present"] is False
    assert report["endpoint"]["bound"] is False
    assert set(report) >= set(contract["requiredSections"])

    for state,category in (("Qualified","healthy-and-qualified"),("Experimental","healthy-but-experimental"),
                           ("Compatible-unqualified","build-compatible-but-live-disabled"),("Unavailable","unavailable"),("Rejected","rejected")):
        q={**query,"compatibilityState":state}
        selected={"status":state,"reason":"fixture","selectedEntry":"entry"}
        assert module.classify(q,selected,{"status":"absent"},{"status":"absent"})["category"]==category
    denied={"status":"indeterminate","reason":"permission-denied"}
    assert module.classify(denied,{"status":"indeterminate"},{"status":"absent"},{"status":"absent"})["category"].startswith("indeterminate")
    interrupted={"status":"ok","value":{"status":"inactive-recovery-required"}}
    assert module.classify(query,{"status":"Compatible-unqualified"},interrupted,{"status":"absent"})["category"]=="rejected"
    assert module.select_manifest_entry({"entries":[]},query)["status"]=="Unavailable"
    duplicate={"entries":[{"id":"entry","route":"GPIO4"},{"id":"entry","route":"GPIO4"}]}
    assert module.select_manifest_entry(duplicate,query)["status"]=="Unavailable"
    exact_missing={"status":"Unavailable","reason":"no-unique-exact-manifest-entry"}
    assert module.classify({**query,"compatibilityState":"Qualified"},exact_missing,{"status":"absent"},{"status":"absent"})["category"]=="unavailable"
    mismatch={"status":"Experimental","reason":"manifest experimental"}
    assert module.classify({**query,"compatibilityState":"Qualified"},mismatch,{"status":"absent"},{"status":"absent"})["category"]=="rejected"

    residue=root/"owned"; residue.mkdir()
    journal={"status":"ok","value":{"status":"inactive-recovery-required","ownedFiles":[{"path":"/owned/file"}],"ownedDirectories":["/owned"]}}
    write(root,"/owned/file","x")
    found=module.Collector(root,runner,kernel)._residue(journal)
    assert found["status"]=="interrupted-operation-residue" and found["paths"]==["/owned","/owned/file"]

source=(ROOT/"scripts/rp1-gpclk-diagnostics.py").read_text()
for prohibited in ("modprobe","dtoverlay","dkms add","dkms build","dkms install","/dev/mem","sign-file"):
    assert prohibited not in source
for required in ("O_RDONLY","QUERY_IOCTL","permission-denied","journalctl","cleanupFaultLatch"):
    assert required in source
operator=(ROOT/"docs/operator/diagnostics.md").read_text()
assert "does not prove absence" in operator
assert commands and all(command[0] in {"dpkg-query","dkms","modinfo","journalctl"} for command in commands)
print("Phase 5.8 diagnostics contracts: PASS")
