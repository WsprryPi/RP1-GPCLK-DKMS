#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the sealed Phase 5.29 Gate D control set entirely offline."""
from __future__ import annotations
import copy, hashlib, json, pathlib, subprocess, sys, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"scripts"))
import gate_d_attempts, gate_d_bootstrap, gate_d_instance, gate_d_preroot, gate_d_root, gate_d_target_plan
COMMIT="c58b541158aa6b8e535becb04c50d41767558793"
def load(relative):
 p=ROOT/relative; assert p.is_file() and not p.is_symlink(); return json.loads(p.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def frozen_payload(relative,expected):
 p=ROOT/relative
 if p.is_file() and sha(p)==expected: return p.read_bytes()
 payload=subprocess.check_output(["git","show",f"{COMMIT}:{relative}"],cwd=ROOT)
 assert hashlib.sha256(payload).hexdigest()==expected
 return payload
envelope=load("release/gate-d-pre-root-bootstrap-envelope-phase5.29-v1.json")
bootstrap=load("release/gate-d-qualification-bootstrap-plan-phase5.29-v1.json")
route=load("release/gate-d-route-compatibility-decision-phase5.29-v1.json")
plan=load("release/gate-d-target-operation-plan-phase5.29-v1.json")
instance=load("release/gate-d-execution-instance-phase5.29-v1.json")
index=load("release/gate-d-attempts-phase5.29-v1/index.json")
assert gate_d_preroot.validate(envelope)=={"valid":True,"readOnly":True,"outputDisabled":True}
assert gate_d_root.validate(instance["qualificationRoot"],verify=False)==pathlib.Path("/home/pi/gate-d-qualification/phase5.29-c58b541158aa")
assert bootstrap["qualificationRoot"]==plan["qualificationRoot"]==index["qualificationRoot"]==instance["qualificationRoot"]
assert route["candidate"]["release"]==instance["candidate"]["release"]==plan["artifacts"]["successor"]["version"]=="0.0.0-phase5.29"
assert route["candidate"]["representativeBuildManifestSha256"]==sha(ROOT/"release/gate-c-representative-build-manifest-phase5.29-v1.json")
assert route["candidate"]["sourceCommit"]==COMMIT
assert route["candidate"]["archiveSha256"]=="7d2516c0a85a56fd7be521c519883c69214cac81759d05efb36352890cefd68e"
assert route["evidence"]["moduleSha256"]=="1d532a063daae542a341e33649a9c87d56e902b781affadeebe0f2025d72d0eb"
assert all(x["state"]=="Compatible-unqualified" and x["liveEligible"] is False for x in route["routes"])
assert instance["inputsReady"] is True and instance["executionReady"] is True
assert instance["authorization"]["approved"] is True
assert instance["authorization"]["targetExecutionApproved"] is True
assert sum(x["status"]=="ready" for x in instance["rows"])==10
assert sum(x["status"]=="deferred-environmental" for x in instance["rows"])==5
roles={x["role"] for x in envelope["releaseInputs"]}
assert roles=={"archive","gpio4Dtbo","gpio20Dtbo","compatibilityManifest","provenance","releaseMetadata","checksums"}
assert len({pathlib.PurePosixPath(x["path"]).parent for x in envelope["releaseInputs"]})==1
sources={x["sourcePath"]:x for x in envelope["transitionFiles"]}; destinations={x["destination"] for x in envelope["transitionFiles"]}; inputs={x["path"]:x["sha256"] for x in envelope["inputFiles"]}
assert len(sources)==len(destinations)==len(envelope["transitionFiles"])==58
assert all(inputs[p]==x["sha256"] for p,x in sources.items())
assert all(inputs[x["path"]]==x["sha256"] for x in envelope["releaseInputs"])
assert sum(x.startswith("release/gate-d-attempts-phase5.29-v1/gd-") for x in destinations)==38
installed={x["path"] for x in envelope["installedTools"]}
assert {x["installedPath"] for x in plan["tooling"].values()}.issubset(installed)
assert {x["installedPath"] for x in plan["pythonModules"].values()}.issubset(installed)
attempt_dir=ROOT/"release/gate-d-attempts-phase5.29-v1"; documents=[]
for record in index["attempts"]:
 p=attempt_dir/record["file"]; assert sha(p)==record["sha256"]; doc=json.loads(p.read_text()); gate_d_attempts.validate_document(doc); result=gate_d_attempts.execute_fake(doc); assert result["status"]=="complete" and result["evidenceSealed"] and result["servicesRestored"] and result["liveOutput"] is False; documents.append(doc)
assert len(documents)==len({x["operationId"] for x in documents})==38
assert len({x["evidenceDirectory"] for x in documents})==38
assert len({x["journal"] for x in documents})==38
assert len({x["inputs"]["stagingDirectory"] for x in documents})==38
assert documents==gate_d_attempts.generate(instance,plan)
assert sum(x["matrixRow"]=="interrupted-upgrade" for x in documents)==15
assert sum(x["matrixRow"]=="removal-open-or-active" for x in documents)==4
with tempfile.TemporaryDirectory() as temporary:
 fake=pathlib.Path(temporary)/"qualification"; fake.mkdir(mode=0o700); marker=fake/instance["qualificationRoot"]["identityFile"]; marker.write_text(json.dumps(envelope["proposedRoot"]["marker"],sort_keys=True,separators=(",",":"))+"\n"); marker.chmod(0o400); assert sha(marker)==instance["qualificationRoot"]["identitySha256"]
 for item in envelope["transitionFiles"]:
  payload=frozen_payload(item["destination"],item["sha256"]); target=fake/item["destination"]; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(payload)
 original=gate_d_root.validate
 def offline(reference,*,verify=True): original(reference,verify=False); return fake
 gate_d_root.validate=offline
 try:
  assert gate_d_bootstrap.validate(bootstrap)["outputDisabled"] is True
  assert gate_d_target_plan.validate(plan)["attemptCount"]==38
  result=gate_d_instance.validate(instance,require_ready=True); assert result["inputsReady"] is True and result["executionReady"] is True and result["blockedRows"]==[] and len(result["deferredRows"])==5
  bad=copy.deepcopy(instance); bad["authorization"]["targetExecutionApproved"]=False; bad["executionReady"]=False
  assert hashlib.sha256((json.dumps(bad,indent=2,sort_keys=True)+"\n").encode()).hexdigest()!=sources["/home/pi/gate-d-inputs/phase5.29-c58b541158aa/control-set/release/gate-d-execution-instance-phase5.29-v1.json"]["sha256"]
 finally: gate_d_root.validate=original
for mutate in (lambda v:v["releaseInputs"].pop(),lambda v:v["releaseInputs"][1].update(role="archive"),lambda v:v["releaseInputs"][1].update(path="/other/rp1-gpclk-gpio4.dtbo"),lambda v:v["transitionFiles"][0].update(sha256="0"*64),lambda v:v["transitionFiles"][1].update(destination=v["transitionFiles"][0]["destination"]),lambda v:v["inputFiles"][0].update(path="/tmp/substituted"),lambda v:v["safety"].update(liveOutput=True)):
 bad=copy.deepcopy(envelope); mutate(bad)
 try: gate_d_preroot.validate(bad)
 except (KeyError,ValueError): continue
 raise AssertionError("adversarial pre-root mutation accepted")
print("Gate D Phase 5.29 offline control set: PASS")
