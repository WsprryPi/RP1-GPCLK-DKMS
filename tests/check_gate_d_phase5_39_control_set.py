#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations
import copy,hashlib,json,pathlib,shutil,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"scripts"))
import gate_d_attempts,gate_d_bootstrap,gate_d_instance,gate_d_preroot,gate_d_root,gate_d_target_plan
def load(p): return json.loads((ROOT/p).read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(v): return hashlib.sha256((json.dumps(v,sort_keys=True,separators=(",",":"))+"\n").encode()).hexdigest()
commit="3768ae9cdccf0c2ae5809603b9a36e73507f2182"
def frozen_payload(relative,expected):
 p=ROOT/relative
 if p.is_file() and sha(p)==expected: return p.read_bytes()
 payload=subprocess.check_output(["git","show",f"{commit}:{relative}"],cwd=ROOT)
 assert hashlib.sha256(payload).hexdigest()==expected
 return payload
route=load("release/gate-d-route-compatibility-decision-phase5.39-v1.json")
plan=load("release/gate-d-target-operation-plan-phase5.39-v1.json")
bootstrap=load("release/gate-d-qualification-bootstrap-plan-phase5.39-v1.json")
instance=load("release/gate-d-execution-instance-phase5.39-v1.json")
envelope=load("release/gate-d-pre-root-bootstrap-envelope-phase5.39-v1.json")
index=load("release/gate-d-attempts-phase5.39-v1/index.json")
identity=load("docs/evidence/gate-d-phase5.39-qualification-install-identity.json")
inventory=load("docs/evidence/gate-d-phase5.39-predecessor-package-inventory.json")
release_inventory=load("docs/evidence/gate-c-phase5.39-release-input-inventory.json")
build=load("release/gate-c-representative-build-manifest-phase5.39-v1.json")
assert route["candidate"]["sourceCommit"]==build["candidate"]["sourceCommit"]==commit
assert route["candidate"]["archiveSha256"]==build["candidate"]["archiveSha256"]
assert route["evidence"]["moduleSha256"]==build["result"]["moduleSha256"]
assert route["candidate"]["representativeBuildManifestSha256"]==sha(ROOT/"release/gate-c-representative-build-manifest-phase5.39-v1.json")
artifacts={x["name"]:x["sha256"] for x in release_inventory["artifacts"]}; assert len(artifacts)==7
assert {x["name"]:x["sha256"] for x in build["result"]["releaseInputs"]}==artifacts
assert build["result"]["releaseInputInventory"]["sha256"]==sha(ROOT/"docs/evidence/gate-c-phase5.39-release-input-inventory.json")
release_inputs={pathlib.PurePosixPath(x["path"]).name:x["sha256"] for x in envelope["releaseInputs"]}
assert release_inputs==artifacts
assert route["candidate"]["archiveSha256"]==artifacts["rp1-gpclk-dkms-0.0.0-phase5.39.tar.gz"]
assert instance["candidate"]["gpio4DtboSha256"]==artifacts["rp1-gpclk-gpio4.dtbo"]
assert instance["candidate"]["gpio20DtboSha256"]==artifacts["rp1-gpclk-gpio20.dtbo"]
assert instance["candidate"]["manifestSha256"]==artifacts["rp1-gpclk-compatibility-manifest.json"]
assert identity["schemaVersion"]==3 and bootstrap["schemaVersion"]==envelope["schemaVersion"]==4
assert bootstrap["packagePaths"]==envelope["installedPackagePaths"]
assert bootstrap["packagePathsSha256"]==envelope["packagePathsSha256"]==canonical(bootstrap["packagePaths"])
typed={x["path"]:x for x in bootstrap["packagePaths"]}; transitions={x["path"]:x for x in identity["packageTransitions"]}; predecessors={x["path"]:x for x in inventory["paths"]}
assert set(typed)==set(transitions)==set(predecessors) and len(typed)==28
assert sum(x["type"]=="file" for x in typed.values())==26 and sum(x["type"]=="symlink" for x in typed.values())==2
for path,item in typed.items():
 t,p=transitions[path],predecessors[path]; assert item["type"]==t["type"]==p["type"]
 assert item["ownerUid"]==t["ownerUid"]==p["ownerUid"]==0 and item["groupGid"]==t["groupGid"]==p["groupGid"]==0
 if item["type"]=="file": assert t["predecessorSha256"]==p["sha256"] and t["successorSha256"]==item["sha256"] and t["mode"]==item["mode"]==p["mode"]
 else: assert t["predecessorTarget"]==p["target"] and t["successorTarget"]==item["target"]
assert envelope["priorTerminalState"]["sha256"]=="24af8111eaa7e9f0c5084dd39063160a5188195a73667b3fcbf115c3c4ea64cf"
assert envelope["priorTerminalState"]["archivePath"].endswith("phase5.37-transaction-recovered.json")
assert all("phase5.36-transaction-recovered.json" not in p and "phase5.34-transaction-recovered.json" not in p for p in envelope["cleanupPaths"])
with tempfile.TemporaryDirectory() as temporary:
 fake=pathlib.Path(temporary)/"qualification"; fake.mkdir(mode=0o700)
 marker=fake/instance["qualificationRoot"]["identityFile"]
 marker.write_text(json.dumps(envelope["proposedRoot"]["marker"],sort_keys=True,separators=(",",":"))+"\n")
 marker.chmod(0o400); assert sha(marker)==instance["qualificationRoot"]["identitySha256"]
 for item in envelope["transitionFiles"]:
  payload=frozen_payload(item["destination"],item["sha256"])
  target=fake/item["destination"]; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(payload)
 original=gate_d_root.validate
 def offline(reference,*,verify=True): original(reference,verify=False); return fake
 gate_d_root.validate=offline
 try:
  assert gate_d_bootstrap.validate(bootstrap)["outputDisabled"] and gate_d_preroot.validate(envelope)["outputDisabled"]
  assert gate_d_target_plan.validate(plan)["attemptCount"]==38
  result=gate_d_instance.validate(instance,require_ready=True); assert result["inputsReady"] is True and result["executionReady"] is True
 finally: gate_d_root.validate=original
assert instance["authorization"]["approved"] is True and instance["authorization"]["targetExecutionApproved"] is True and instance["executionReady"] is True
attempt_dir=ROOT/"release/gate-d-attempts-phase5.39-v1"; documents=[]
for record in index["attempts"]:
 p=attempt_dir/record["file"]; assert sha(p)==record["sha256"]
 d=json.loads(p.read_text()); gate_d_attempts.validate_document(d); result=gate_d_attempts.execute_fake(d)
 assert result["status"]=="complete" and result["evidenceSealed"] and result["servicesRestored"] and result["liveOutput"] is False; documents.append(d)
assert len(documents)==38 and documents==gate_d_attempts.generate(instance,plan)
assert sum(x["matrixRow"]=="interrupted-upgrade" for x in documents)==15 and sum(x["matrixRow"]=="removal-open-or-active" for x in documents)==4
inputs={x["path"]:x["sha256"] for x in envelope["inputFiles"]}; assert len(inputs)==len(envelope["inputFiles"])
for x in envelope["transitionFiles"]: assert inputs[x["sourcePath"]]==x["sha256"]
for x in envelope["releaseInputs"]: assert inputs[x["path"]]==x["sha256"]
assert inputs[envelope["qualificationIdentity"]["path"]]==sha(ROOT/"docs/evidence/gate-d-phase5.39-qualification-install-identity.json")
with tempfile.TemporaryDirectory() as temporary:
 installed=pathlib.Path(temporary)/"usr/libexec/rp1-gpclk-dkms"; installed.mkdir(parents=True)
 for name in ("gate_d_root","gate_d_bootstrap","gate_d_target_plan","gate_d_lifecycle","gate_d_outer","gate_d_attempts","gate_d_instance","gate_d_preroot"): shutil.copy2(ROOT/"scripts"/f"{name}.py",installed/f"{name}.py")
 executor=installed/"gate-d-executor"; shutil.copy2(ROOT/"scripts/gate_d_outer.py",executor); executor.chmod(0o755)
 for record in index["attempts"]:
  for action in ("validate","plan"):
   result=subprocess.run([str(executor),action,str(attempt_dir/record["file"])],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True); assert result.returncode==0 and "Traceback" not in result.stderr
for mutate in (lambda v:v["installedPackagePaths"].pop(),lambda v:v["installedPackagePaths"][0].update(type="symlink"),lambda v:v.update(packagePathsSha256="0"*64),lambda v:v["priorTerminalState"].update(liveOutput=True),lambda v:v["safety"].update(gpioAccess=True)):
 bad=copy.deepcopy(envelope); mutate(bad)
 try: gate_d_preroot.validate(bad)
 except (KeyError,ValueError): pass
 else: raise AssertionError("unsafe Phase 5.39 envelope accepted")
subprocess.run([sys.executable,str(ROOT/"scripts/generate_phase5_39_control_set.py"),"--check"],check=True)
print("Gate D Phase 5.39 offline control set: PASS")
