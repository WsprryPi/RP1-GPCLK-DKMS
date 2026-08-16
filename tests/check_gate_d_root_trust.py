#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations
import copy, hashlib, importlib.util, json, os, pathlib, shutil, sys, tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temporary:
    base=pathlib.Path(temporary).resolve(); root=base/"qualification"; scripts=root/"scripts"; release=root/"release"
    scripts.mkdir(parents=True); release.mkdir(); root.chmod(0o700)
    outer=scripts/"gate_d_outer.py"; validator=scripts/"gate_d_root.py"
    shutil.copy2(ROOT/"scripts/gate_d_outer.py",outer); shutil.copy2(ROOT/"scripts/gate_d_root.py",validator)
    marker={"SPDX-License-Identifier":"MIT","schemaVersion":1,"kind":"gate-d-qualification-root-identity","rootPath":str(root),"candidateRelease":"0.0.0-phase5.23","sourceCommit":"1"*40}
    marker_path=root/".gate-d-root.json"; marker_path.write_text(json.dumps(marker,sort_keys=True)+"\n")
    reference={"path":str(root),"identityFile":marker_path.name,"identitySha256":hashlib.sha256(marker_path.read_bytes()).hexdigest(),"ownerUid":os.getuid(),"mode":"0700"}
    def identity(source:pathlib.Path,installed:str):
        sha=hashlib.sha256(source.read_bytes()).hexdigest(); return {"sourcePath":str(source.relative_to(root)),"installedPath":installed,"sourceSha256":sha,"installedSha256":sha,"installKind":"copied","candidateArchiveMember":True}
    plan={"schemaVersion":4,"qualificationRoot":reference,"tooling":{"rootValidator":identity(validator,"/usr/libexec/rp1-gpclk-dkms/gate_d_root.py"),"permanentExecutor":identity(outer,"/usr/libexec/rp1-gpclk-dkms/gate-d-executor")}}
    plan_path=release/"plan.json"; plan_path.write_text(json.dumps(plan,sort_keys=True)+"\n")
    instance={"schemaVersion":3,"kind":"gate-d-representative-system-execution-instance","qualificationRoot":reference,"executionPolicy":{"targetPlan":"release/plan.json","targetPlanSha256":hashlib.sha256(plan_path.read_bytes()).hexdigest()}}
    instance_path=release/"instance.json"; instance_path.write_text(json.dumps(instance,sort_keys=True)+"\n")
    spec=importlib.util.spec_from_file_location("installed_gate_d_outer",outer); assert spec and spec.loader
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)
    loaded,loaded_root=module.bootstrap_root_validator(instance_path); assert loaded==instance and loaded_root==root
    mutations=[]
    missing=copy.deepcopy(plan); missing["tooling"].pop("rootValidator"); mutations.append(missing)
    extra=copy.deepcopy(plan); extra["tooling"]["rootValidator"]["extra"]=True; mutations.append(extra)
    wrong_path=copy.deepcopy(plan); wrong_path["tooling"]["rootValidator"]["installedPath"]="/tmp/root.py"; mutations.append(wrong_path)
    wrong_source=copy.deepcopy(plan); wrong_source["tooling"]["rootValidator"]["sourceSha256"]="0"*64; mutations.append(wrong_source)
    wrong_installed=copy.deepcopy(plan); wrong_installed["tooling"]["rootValidator"]["installedSha256"]="0"*64; mutations.append(wrong_installed)
    for number,bad_plan in enumerate(mutations):
        bad_path=release/f"bad-{number}.json"; bad_path.write_text(json.dumps(bad_plan,sort_keys=True)+"\n")
        bad_instance=copy.deepcopy(instance); bad_instance["executionPolicy"]={"targetPlan":str(bad_path.relative_to(root)),"targetPlanSha256":hashlib.sha256(bad_path.read_bytes()).hexdigest()}
        bad_instance_path=release/f"bad-instance-{number}.json"; bad_instance_path.write_text(json.dumps(bad_instance,sort_keys=True)+"\n")
        try: module.bootstrap_root_validator(bad_instance_path)
        except ValueError: pass
        else: raise AssertionError("unsafe root-validator trust identity accepted")
    original=validator.read_bytes(); validator.write_bytes(original+b"\n# substitution\n")
    try: module.bootstrap_root_validator(instance_path)
    except ValueError as error: assert "bytes differ" in str(error)
    else: raise AssertionError("post-bootstrap root-validator substitution accepted")
    validator.write_bytes(original); link=scripts/"root-link.py"; link.symlink_to(validator)
    symlink_plan=copy.deepcopy(plan); symlink_plan["tooling"]["rootValidator"]["sourcePath"]=str(link.relative_to(root)); symlink_path=release/"symlink-plan.json"; symlink_path.write_text(json.dumps(symlink_plan,sort_keys=True)+"\n")
    symlink_instance=copy.deepcopy(instance); symlink_instance["executionPolicy"]={"targetPlan":str(symlink_path.relative_to(root)),"targetPlanSha256":hashlib.sha256(symlink_path.read_bytes()).hexdigest()}; symlink_instance_path=release/"symlink-instance.json"; symlink_instance_path.write_text(json.dumps(symlink_instance,sort_keys=True)+"\n")
    try: module.bootstrap_root_validator(symlink_instance_path)
    except ValueError: pass
    else: raise AssertionError("symlinked root-validator source accepted")
    alias=root/"release-link"; alias.symlink_to(release,target_is_directory=True)
    parent_instance=copy.deepcopy(instance); parent_instance["executionPolicy"]={"targetPlan":"release-link/plan.json","targetPlanSha256":hashlib.sha256(plan_path.read_bytes()).hexdigest()}; parent_path=release/"parent-symlink-instance.json"; parent_path.write_text(json.dumps(parent_instance,sort_keys=True)+"\n")
    try: module.bootstrap_root_validator(parent_path)
    except ValueError: pass
    else: raise AssertionError("symlinked target-plan parent accepted")
    bad_marker=copy.deepcopy(marker); bad_marker["kind"]="wrong-kind"; marker_path.write_text(json.dumps(bad_marker,sort_keys=True)+"\n")
    bad_reference=copy.deepcopy(reference); bad_reference["identitySha256"]=hashlib.sha256(marker_path.read_bytes()).hexdigest()
    marker_plan=copy.deepcopy(plan); marker_plan["qualificationRoot"]=bad_reference; marker_plan_path=release/"marker-plan.json"; marker_plan_path.write_text(json.dumps(marker_plan,sort_keys=True)+"\n")
    marker_instance=copy.deepcopy(instance); marker_instance["qualificationRoot"]=bad_reference; marker_instance["executionPolicy"]={"targetPlan":str(marker_plan_path.relative_to(root)),"targetPlanSha256":hashlib.sha256(marker_plan_path.read_bytes()).hexdigest()}; marker_instance_path=release/"marker-instance.json"; marker_instance_path.write_text(json.dumps(marker_instance,sort_keys=True)+"\n")
    try: module.bootstrap_root_validator(marker_instance_path)
    except ValueError as error: assert "marker identity" in str(error)
    else: raise AssertionError("semantically invalid root marker accepted")
print("Gate D pre-import root-validator trust: PASS")
