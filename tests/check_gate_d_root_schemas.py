#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations
import copy, json, pathlib, subprocess, tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
root={"path":"/home/pi/gate-d-qualification/phase5.24","identityFile":".gate-d-root.json","identitySha256":"1"*64,"ownerUid":1000,"mode":"0700"}
bootstrap={"SPDX-License-Identifier":"MIT","schemaVersion":3,"kind":"gate-d-qualification-bootstrap-plan","operationId":"x","hostId":"h","qualificationRoot":root,"predecessorVersion":"p","kernelRelease":"k","stagingDirectory":"/s","candidate":{},"qualificationIdentity":{},"administrator":{},"argv":[],"cleanupArgv":[],"recoveryArgv":[],"journal":"/j","deadlineSeconds":1,"expectedPreState":{},"expectedPostState":{},"retainedTools":[{}],"cleanupPaths":["/c"],"safety":{}}
module={"sourcePath":"scripts/gate_d_root.py","installedPath":"/usr/libexec/rp1-gpclk-dkms/gate_d_root.py","sourceSha256":"2"*64,"installedSha256":"2"*64,"installKind":"copied","candidateArchiveMember":True}
names=("gate_d_root","gate_d_bootstrap","gate_d_target_plan","gate_d_lifecycle","gate_d_outer","gate_d_attempts","gate_d_instance","gate_d_preroot")
modules={name:{**module,"sourcePath":f"scripts/{name}.py","installedPath":f"/usr/libexec/rp1-gpclk-dkms/{name}.py"} for name in names}; modules["gate_d_root"]=module
target={"SPDX-License-Identifier":"MIT","schemaVersion":5,"kind":"gate-d-output-disabled-target-operation-plan","qualificationRoot":root,"qualificationBootstrap":{},"hostId":"h","tooling":{},"pythonModules":modules,"invariants":{},"services":[],"artifacts":{},"boot":{},"attemptEnvelope":["create-evidence"],"rows":[]}
index={"SPDX-License-Identifier":"MIT","schemaVersion":2,"kind":"gate-d-attempt-index","qualificationRoot":root,"attemptCount":38,"executors":{},"attempts":[{}]*38}
instance=json.loads((ROOT/"release/gate-d-execution-instance-v1.json").read_text()); instance["schemaVersion"]=4; instance["qualificationRoot"]=root
instance["executionPolicy"]["qualificationBootstrap"]="release/bootstrap.json"; instance["executionPolicy"]["qualificationBootstrapSha256"]="6"*64
cases=(("gate-d-qualification-bootstrap-plan-v1.schema.json",bootstrap),("gate-d-target-plan-v1.schema.json",target),("gate-d-attempt-index-v1.schema.json",index),("gate-d-execution-instance-v1.schema.json",instance))

def accepted(schema:str,value:dict)->bool:
    with tempfile.NamedTemporaryFile("w",suffix=".json") as document:
        json.dump(value,document); document.flush()
        schema_path=ROOT/"schema"/schema
        result=subprocess.run(["check-jsonschema","--base-uri",schema_path.as_uri(),"--schemafile",str(schema_path),document.name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return result.returncode==0

definition=json.loads((ROOT/"schema/gate-d-qualification-root-v1.schema.json").read_text())
assert definition["additionalProperties"] is False and set(definition["required"])==set(root)
for schema,value in cases:
    assert accepted(schema,value), schema
    missing=copy.deepcopy(value); missing.pop("qualificationRoot"); assert not accepted(schema,missing)
    extra=copy.deepcopy(value); extra["qualificationRoot"]["extra"]=True; assert not accepted(schema,extra)
    for field,bad_value in (("path","relative"),("path","/safe/../escape"),("path","/usr"),("identityFile","dir/marker"),("identitySha256","0"*63),("ownerUid",-1),("mode","0755")):
        bad=copy.deepcopy(value); bad["qualificationRoot"][field]=bad_value; assert not accepted(schema,bad),(schema,field)
for schema,value,old_version in ((cases[0][0],bootstrap,1),(cases[1][0],target,3),(cases[2][0],index,1),(cases[3][0],instance,2)):
    old=copy.deepcopy(value); old["schemaVersion"]=old_version; old.pop("qualificationRoot")
    if schema=="gate-d-target-plan-v1.schema.json": old.pop("pythonModules")
    assert accepted(schema,old),schema
    stale=copy.deepcopy(old); stale["qualificationRoot"]=root; assert not accepted(schema,stale),schema
target4=copy.deepcopy(target); target4["schemaVersion"]=4; target4.pop("pythonModules")
assert accepted("gate-d-target-plan-v1.schema.json",target4)
target4["pythonModules"]=modules
assert not accepted("gate-d-target-plan-v1.schema.json",target4)
legacy=copy.deepcopy(instance); legacy["schemaVersion"]=1; legacy.pop("qualificationRoot"); legacy["executionPolicy"].pop("qualificationBootstrap"); legacy["executionPolicy"].pop("qualificationBootstrapSha256"); assert accepted(cases[3][0],legacy)
legacy["executionPolicy"]["qualificationBootstrap"]="unexpected"; assert not accepted(cases[3][0],legacy)
print("Gate D qualification-root JSON Schemas: PASS")
