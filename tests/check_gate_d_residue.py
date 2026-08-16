#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations
import copy, hashlib, importlib.util, json, pathlib, tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("gate_d_residue",ROOT/"scripts/gate_d_residue.py"); assert spec and spec.loader
tool=importlib.util.module_from_spec(spec); spec.loader.exec_module(tool)
base_document=json.loads((ROOT/"release/gate-d-phase5.24-residue-recovery-v1.json").read_text())
baseline=tool.BASELINE
assert tool.validate(base_document)["outputDisabled"] is True
for mutation in (
    lambda v:v.update(host="other"), lambda v:v.update(candidate="0.0.0-phase5.25"),
    lambda v:v["marker"].update(sha256="0"*63), lambda v:v["journal"].update(path="relative"),
    lambda v:v["administratorState"].update(expected="present"),
    lambda v:v["safety"].update(gpioAccess=True), lambda v:v["preservedPaths"].clear(),
):
    bad=copy.deepcopy(base_document); mutation(bad)
    try: tool.validate(bad)
    except ValueError: pass
    else: raise AssertionError("unsafe residue-recovery document accepted")

def place(prefix:pathlib.Path, document:dict, *, extra=False):
    root=prefix/document["root"].lstrip("/"); root.mkdir(parents=True)
    marker=root/".gate-d-root.json"; marker.write_text('{"fixture":"marker"}\n')
    document["marker"]["sha256"]=hashlib.sha256(marker.read_bytes()).hexdigest()
    journal=prefix/document["journal"]["path"].lstrip("/"); journal.parent.mkdir(parents=True); journal.write_text('{"fixture":"journal"}\n')
    document["journal"]["sha256"]=hashlib.sha256(journal.read_bytes()).hexdigest()
    if extra: (root/"foreign").write_text("preserve\n")
    preserved=prefix/document["preservedPaths"][0].lstrip("/"); preserved.mkdir(parents=True); (preserved/"evidence").write_text("keep\n")
    return root,marker,journal,preserved

with tempfile.TemporaryDirectory() as temporary:
    document=copy.deepcopy(base_document); prefix=pathlib.Path(temporary); root,marker,journal,preserved=place(prefix,document)
    assert tool.execute(document,prefix=prefix,probe=lambda:baseline)["status"]=="ready"
    assert tool.execute(document,prefix=prefix,probe=lambda:baseline,execute=True)["status"]=="complete"
    assert preserved.joinpath("evidence").read_text()=="keep\n"
    assert tool.execute(document,prefix=prefix,probe=lambda:baseline,execute=True)["status"]=="already-clean"

for failure in ("marker", "journal", "admin", "extra", "baseline", "symlink"):
    with tempfile.TemporaryDirectory() as temporary:
        document=copy.deepcopy(base_document); prefix=pathlib.Path(temporary); root,marker,journal,preserved=place(prefix,document,extra=failure=="extra")
        if failure=="marker": marker.write_text("changed\n")
        elif failure=="journal": journal.write_text("changed\n")
        elif failure=="admin": admin=prefix/document["administratorState"]["path"].lstrip("/"); admin.parent.mkdir(parents=True,exist_ok=True); admin.write_text("foreign\n")
        elif failure=="symlink": marker.unlink(); marker.symlink_to(preserved/"evidence")
        changed=dict(baseline); changed["moduleLoaded"]=True
        try: tool.execute(document,prefix=prefix,probe=lambda:changed if failure=="baseline" else baseline,execute=True)
        except ValueError: pass
        else: raise AssertionError(f"unsafe residue recovery accepted: {failure}")
        assert preserved.joinpath("evidence").read_text()=="keep\n"
print("Gate D failed pre-root residue recovery: PASS")
