#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations
import copy, hashlib, importlib.util, importlib.machinery, json, os, pathlib, shutil, sys, tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
MODULES=("gate_d_root","gate_d_bootstrap","gate_d_target_plan","gate_d_lifecycle","gate_d_outer","gate_d_attempts","gate_d_instance","gate_d_preroot")
INSTALLED={name:f"/usr/libexec/rp1-gpclk-dkms/{name}.py" for name in MODULES}
def sha(path:pathlib.Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()

with tempfile.TemporaryDirectory() as temporary:
    base=pathlib.Path(temporary).resolve(); qualification=base/"qualification"; scripts=qualification/"scripts"; release=qualification/"release"; fake_root=base/"installed"
    scripts.mkdir(parents=True); release.mkdir(); qualification.chmod(0o700)
    for name in MODULES:
        shutil.copy2(ROOT/"scripts"/f"{name}.py",scripts/f"{name}.py")
        destination=fake_root/INSTALLED[name].lstrip("/"); destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/"scripts"/f"{name}.py",destination); destination.chmod(0o644)
    installed_executor=fake_root/"usr/libexec/rp1-gpclk-dkms/gate-d-executor"
    shutil.copy2(ROOT/"scripts/gate_d_outer.py",installed_executor); installed_executor.chmod(0o755)
    marker={"SPDX-License-Identifier":"MIT","schemaVersion":1,"kind":"gate-d-qualification-root-identity","rootPath":str(qualification),"candidateRelease":"0.0.0-phase5.29","sourceCommit":"1"*40}
    marker_path=qualification/".gate-d-root.json"; marker_path.write_text(json.dumps(marker,sort_keys=True)+"\n")
    reference={"path":str(qualification),"identityFile":marker_path.name,"identitySha256":sha(marker_path),"ownerUid":os.getuid(),"mode":"0700"}
    def identity(name:str)->dict:
        source=scripts/f"{name}.py"
        return {"sourcePath":f"scripts/{name}.py","installedPath":INSTALLED[name],"sourceSha256":sha(source),"installedSha256":sha(source),"installKind":"copied","candidateArchiveMember":True}
    graph={name:identity(name) for name in MODULES}; executor_identity=identity("gate_d_outer"); executor_identity["installedPath"]="/usr/libexec/rp1-gpclk-dkms/gate-d-executor"
    plan={"schemaVersion":5,"qualificationRoot":reference,"pythonModules":graph,"tooling":{"rootValidator":graph["gate_d_root"],"permanentExecutor":executor_identity}}
    plan_path=release/"plan.json"; plan_path.write_text(json.dumps(plan,sort_keys=True)+"\n")
    instance={"schemaVersion":4,"kind":"gate-d-representative-system-execution-instance","qualificationRoot":reference,"executionPolicy":{"targetPlan":"release/plan.json","targetPlanSha256":sha(plan_path)}}
    instance_path=release/"instance.json"; instance_path.write_text(json.dumps(instance,sort_keys=True)+"\n")
    loader=importlib.machinery.SourceFileLoader("installed_gate_d_executor",str(installed_executor))
    spec=importlib.util.spec_from_loader(loader.name,loader); assert spec and spec.loader
    executor=importlib.util.module_from_spec(spec); sys.modules[spec.name]=executor; spec.loader.exec_module(executor)
    override=pathlib.Path("/usr/libexec/rp1-gpclk-dkms/gate-d-executor")
    loaded,loaded_root=executor.bootstrap_root_validator(instance_path,installed_root=fake_root,current_executor_override=override)
    assert loaded==instance and loaded_root==qualification and set(MODULES).issubset(sys.modules)
    attempt=json.loads((ROOT/"release/gate-d-attempts-phase5.16-v1/gd-current-supported-kernel-gpio4.json").read_text())
    sys.modules["gate_d_attempts"].validate_document(attempt); assert sys.modules["gate_d_outer"].ClosedDispatcher(attempt).plan()
    for name in MODULES:
        absent=fake_root/INSTALLED[name].lstrip("/"); original_absent=absent.read_bytes(); absent.unlink()
        try: executor.bootstrap_root_validator(instance_path,installed_root=fake_root,current_executor_override=override)
        except ValueError: pass
        else: raise AssertionError(f"missing installed module accepted: {name}")
        absent.write_bytes(original_absent); absent.chmod(0o644)
    victim=fake_root/INSTALLED["gate_d_bootstrap"].lstrip("/"); original=victim.read_bytes()
    for mode in ("missing","swapped","symlink","writable","substituted"):
        victim.unlink()
        if mode=="swapped": victim.write_bytes((fake_root/INSTALLED["gate_d_instance"].lstrip("/")).read_bytes())
        elif mode=="symlink": victim.symlink_to(scripts/"gate_d_bootstrap.py")
        elif mode in {"writable","substituted"}:
            victim.write_bytes(original+(b"\n# changed\n" if mode=="substituted" else b"")); victim.chmod(0o666 if mode=="writable" else 0o644)
        try: executor.bootstrap_root_validator(instance_path,installed_root=fake_root,current_executor_override=override)
        except ValueError: pass
        else: raise AssertionError(f"unsafe installed module accepted: {mode}")
        if victim.is_symlink() or victim.exists(): victim.unlink()
        victim.write_bytes(original); victim.chmod(0o644)
    extra=copy.deepcopy(plan); extra["pythonModules"]["gate_d_extra"]=identity("gate_d_root")
    extra_path=release/"extra.json"; extra_path.write_text(json.dumps(extra,sort_keys=True)+"\n")
    extra_instance=copy.deepcopy(instance); extra_instance["executionPolicy"]={"targetPlan":"release/extra.json","targetPlanSha256":sha(extra_path)}
    extra_instance_path=release/"extra-instance.json"; extra_instance_path.write_text(json.dumps(extra_instance,sort_keys=True)+"\n")
    try: executor.bootstrap_root_validator(extra_instance_path,installed_root=fake_root,current_executor_override=override)
    except ValueError: pass
    else: raise AssertionError("extra installed module identity accepted")
    unbound=fake_root/INSTALLED["gate_d_instance"].lstrip("/"); unbound_original=unbound.read_bytes()
    unbound.write_bytes(unbound_original+b"\nimport gate_d_unbound\n"); unbound.chmod(0o644)
    unbound_plan=copy.deepcopy(plan); changed=sha(unbound)
    unbound_plan["pythonModules"]["gate_d_instance"]["sourceSha256"]=changed
    unbound_plan["pythonModules"]["gate_d_instance"]["installedSha256"]=changed
    unbound_path=release/"unbound.json"; unbound_path.write_text(json.dumps(unbound_plan,sort_keys=True)+"\n")
    unbound_instance=copy.deepcopy(instance); unbound_instance["executionPolicy"]={"targetPlan":"release/unbound.json","targetPlanSha256":sha(unbound_path)}
    unbound_instance_path=release/"unbound-instance.json"; unbound_instance_path.write_text(json.dumps(unbound_instance,sort_keys=True)+"\n")
    try: executor.bootstrap_root_validator(unbound_instance_path,installed_root=fake_root,current_executor_override=override)
    except ValueError: pass
    else: raise AssertionError("unbound transitive import accepted")
    unbound.write_bytes(unbound_original+b"\nraise RuntimeError('injected initialization failure')\n"); unbound.chmod(0o644)
    failure_plan=copy.deepcopy(plan); changed=sha(unbound)
    failure_plan["pythonModules"]["gate_d_instance"]["sourceSha256"]=changed
    failure_plan["pythonModules"]["gate_d_instance"]["installedSha256"]=changed
    failure_path=release/"failure.json"; failure_path.write_text(json.dumps(failure_plan,sort_keys=True)+"\n")
    failure_instance=copy.deepcopy(instance); failure_instance["executionPolicy"]={"targetPlan":"release/failure.json","targetPlanSha256":sha(failure_path)}
    failure_instance_path=release/"failure-instance.json"; failure_instance_path.write_text(json.dumps(failure_instance,sort_keys=True)+"\n")
    prior={name:sys.modules[name] for name in MODULES}
    try: executor.bootstrap_root_validator(failure_instance_path,installed_root=fake_root,current_executor_override=override)
    except RuntimeError: pass
    else: raise AssertionError("module initialization failure accepted")
    assert all(sys.modules[name] is prior[name] for name in MODULES)
print("Gate D exact installed Python import graph: PASS")
