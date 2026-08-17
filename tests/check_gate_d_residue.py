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
    lambda v:v.update(host="other"), lambda v:v.update(candidate="0.0.0-phase5.51"),
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

attempt_recovery=json.loads((ROOT/"release/gate-d-phase5.39-first-attempt-terminal-recovery-v1.json").read_text())
assert tool.validate(attempt_recovery)["outputDisabled"] is True
for mutation in (
    lambda v:v["expectedFailure"].update(nextStep=2),
    lambda v:v["expectedFailure"].update(pendingOperation="install-successor"),
    lambda v:v["destination"].update(evidenceDirectory=v["source"]["evidenceDirectory"]),
    lambda v:v["safety"].update(gpioAccess=True),
):
    bad=copy.deepcopy(attempt_recovery); mutation(bad)
    try: tool.validate(bad)
    except ValueError: pass
    else: raise AssertionError("unsafe failed-attempt recovery accepted")

with tempfile.TemporaryDirectory() as temporary:
    prefix=pathlib.Path(temporary); document=copy.deepcopy(attempt_recovery)
    source=prefix/document["source"]["evidenceDirectory"].lstrip("/"); source.mkdir(parents=True)
    journal=source/"transaction.json"
    journal_value={
        "status":"inactive-recovery-required","sealed":True,"recoveryRequired":True,
        "liveOutput":False,"operationId":document["expectedFailure"]["operationId"],
        "documentSha256":document["expectedFailure"]["documentSha256"],
        "indexSha256":document["expectedFailure"]["indexSha256"],
        "executorSha256":document["expectedFailure"]["executorSha256"],
        "failure":"CalledProcessError","nextStep":1,
        "records":[{"operation":"create-evidence","status":0},
                   {"operation":"capture-preflight","status":"pending"}],
    }
    journal.write_text(json.dumps(journal_value,indent=2,sort_keys=True)+"\n"); journal.chmod(0o400)
    manifest=source/"SHA256SUMS"; manifest.write_text(f"{hashlib.sha256(journal.read_bytes()).hexdigest()}  transaction.json\n"); manifest.chmod(0o400); source.chmod(0o500)
    document["source"]["journalSha256"]=hashlib.sha256(journal.read_bytes()).hexdigest()
    document["source"]["manifestSha256"]=hashlib.sha256(manifest.read_bytes()).hexdigest()
    assert tool.execute(document,prefix=prefix,probe=lambda:baseline)["status"]=="ready"
    result=tool.execute(document,prefix=prefix,probe=lambda:baseline,execute=True)
    assert result["status"]=="complete" and journal.read_text()==json.dumps(journal_value,indent=2,sort_keys=True)+"\n"
    destination=prefix/document["destination"]["evidenceDirectory"].lstrip("/")
    terminal=json.loads((destination/"transaction.json").read_text())
    assert terminal["status"]=="complete" and terminal["recoveryRequired"] is False and terminal["liveOutput"] is False
    assert destination.stat().st_mode&0o777==0o500 and all(p.stat().st_mode&0o777==0o400 for p in destination.iterdir())

retirement=json.loads((ROOT/"release/gate-d-phase5.42-first-attempt-evidence-retirement-v1.json").read_text())
assert tool.validate(retirement)["outputDisabled"] is True
for mutation in (
    lambda v:v.update(candidate="0.0.0-phase5.51"),
    lambda v:v["source"]["journal"].update(sha256="0"*63),
    lambda v:v["destination"].update(evidenceDirectory=v["source"]["evidenceDirectory"]),
    lambda v:v["destination"].update(evidenceDirectory="/var/lib/rp1-gpclk-dkms/gate-d/history/other/evidence"),
    lambda v:v["safety"].update(gpioAccess=True),
):
    bad=copy.deepcopy(retirement); mutation(bad)
    try: tool.validate(bad)
    except ValueError: pass
    else: raise AssertionError("unsafe failed-attempt evidence retirement accepted")

with tempfile.TemporaryDirectory() as temporary:
    prefix=pathlib.Path(temporary); document=copy.deepcopy(retirement)
    source=prefix/document["source"]["evidenceDirectory"].lstrip("/"); source.mkdir(parents=True)
    journal=source/"transaction.json"
    expected=document["expectedFailure"]
    journal_value={
        "status":"inactive-recovery-required","sealed":True,"recoveryRequired":True,
        "liveOutput":False,"operationId":expected["operationId"],
        "documentSha256":expected["documentSha256"],"indexSha256":expected["indexSha256"],
        "executorSha256":expected["executorSha256"],"failure":"CalledProcessError","nextStep":1,
        "records":[{"operation":"create-evidence","status":0},
                   {"operation":"capture-preflight","status":"pending"}],
    }
    journal.write_text(json.dumps(journal_value,indent=2,sort_keys=True)+"\n"); journal.chmod(0o400)
    manifest=source/"SHA256SUMS"; manifest.write_text(f"{hashlib.sha256(journal.read_bytes()).hexdigest()}  transaction.json\n"); manifest.chmod(0o400); source.chmod(0o500)
    document["source"]["journal"]["sha256"]=hashlib.sha256(journal.read_bytes()).hexdigest()
    document["source"]["manifest"]["sha256"]=hashlib.sha256(manifest.read_bytes()).hexdigest()
    def fixture_rename(source_path,destination_path):
        source_path.chmod(0o700); source_path.rename(destination_path); destination_path.chmod(0o500)
    execute_retirement=lambda execute=False:tool.execute_evidence_retirement(
        document,prefix=prefix,probe=lambda:baseline,execute=execute,
        expected_owner_uid=source.stat().st_uid,expected_owner_gid=source.stat().st_gid,
        rename=fixture_rename)
    assert execute_retirement()["status"]=="ready"
    result=execute_retirement(execute=True)
    destination=prefix/document["destination"]["evidenceDirectory"].lstrip("/")
    assert result["status"]=="complete" and not source.exists() and destination.is_dir()
    assert hashlib.sha256((destination/"transaction.json").read_bytes()).hexdigest()==document["source"]["journal"]["sha256"]
    assert hashlib.sha256((destination/"SHA256SUMS").read_bytes()).hexdigest()==document["source"]["manifest"]["sha256"]
print("Gate D failed pre-root residue recovery: PASS")
