#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gate_d_target_plan", ROOT / "scripts/gate_d_target_plan.py")
assert spec and spec.loader
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
plan = json.loads((ROOT / "release/gate-d-target-operation-plan-v1.json").read_text())
result = tool.validate(plan, verify_tools=False)
assert result == {"valid": True, "readOnly": True, "rowCount": 10, "attemptCount": 38, "liveOutput": False}
try:
    tool.validate(plan)
except ValueError as error:
    assert "legacy target plan" in str(error)
else:
    raise AssertionError("superseded Phase 5.14 plan was accepted for execution")
assert plan["artifacts"]["successor"] == {
    "version": "0.0.0-phase5.14",
    "archive": "/home/pi/gate-d-inputs/phase5.14-7bbdfe1b5c83/rp1-gpclk-dkms-0.0.0-phase5.14.tar.gz",
    "sha256": "d0c17f2842716052bb49b1a4fc079d3d48a5674bae8610eee2ab9d17ac548bea",
}

for mutation in (
    lambda value: value["invariants"].update(liveOutput=True),
    lambda value: value["boot"].update(tryboot="/boot/firmware/config.txt"),
    lambda value: value["services"].pop(),
    lambda value: value["tooling"]["bootSelector"].update(sha256="0" * 63),
    lambda value: value["artifacts"]["successor"].update(version="0.0.0-phase5.2"),
    lambda value: value["rows"][4]["attempts"].pop(),
    lambda value: value["rows"][8]["actions"].remove("start-busy-injector-and-wait-ready"),
    lambda value: value["rows"][0]["actions"].append("live_output=1"),
):
    bad = copy.deepcopy(plan)
    mutation(bad)
    try:
        tool.validate(bad, verify_tools=False)
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe or incomplete Gate D target plan accepted")

# Schema 2 separates immutable source bytes from installed executable bytes.
current = copy.deepcopy(plan)
current["schemaVersion"] = 2
for item in current["tooling"].values():
    source_sha = __import__("hashlib").sha256((ROOT / item["sourcePath"]).read_bytes()).hexdigest()
    item.pop("sha256")
    item["sourceSha256"] = source_sha
    item["installKind"] = "target-built" if item["sourcePath"].endswith(".c") else "copied"
    item["installedSha256"] = "a" * 64 if item["installKind"] == "target-built" else source_sha
assert tool.validate(current)["attemptCount"] == 38
bootstrap_value={"SPDX-License-Identifier":"MIT","schemaVersion":1,"kind":"gate-d-qualification-bootstrap-plan","operationId":"test-bootstrap","hostId":"test","predecessorVersion":"0.0.0-phase5.2","kernelRelease":"test-kernel","stagingDirectory":"/var/lib/rp1-gpclk-dkms/gate-d/bootstrap","candidate":{"release":"0.0.0-phase5.18","sourceCommit":"1"*40,"archive":"/inputs/candidate.tar.gz","archiveSha256":"2"*64},"qualificationIdentity":{"path":"/inputs/identity.json","sha256":"3"*64},"administrator":{"sourcePath":"scripts/rp1-gpclk-admin.py","sourceSha256":"4"*64,"bootstrapPath":"/inputs/extracted/scripts/rp1-gpclk-admin.py","installedPath":"/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-admin","installedSha256":"4"*64},"argv":["/usr/bin/python3","/inputs/extracted/scripts/rp1-gpclk-admin.py","install","--execute","--release-directory","/inputs","--route","gpio4","--qualification-install","--qualification-identity","/inputs/identity.json"],"cleanupArgv":["/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle","dispatch","complete-removal","0.0.0-phase5.2","0.0.0-phase5.18","test-kernel","/var/lib/rp1-gpclk-dkms/gate-d/bootstrap","--execute"],"recoveryArgv":["/usr/bin/python3","/inputs/extracted/scripts/rp1-gpclk-admin.py","recover","--execute"],"journal":"/var/lib/rp1-gpclk-dkms/gate-d/bootstrap.json","deadlineSeconds":1800,"expectedPreState":{"moduleLoaded":False,"endpointPresent":False,"overlayActive":False,"dkmsTestVersions":False,"liveOutput":False},"expectedPostState":{"moduleLoaded":False,"endpointPresent":False,"overlayActive":False,"dkmsTestVersions":False,"liveOutput":False},"retainedTools":[{"path":"/usr/libexec/rp1-gpclk-dkms/gate-d-executor","sha256":"5"*64}],"cleanupPaths":["/var/lib/rp1-gpclk-dkms/gate-d/bootstrap"],"safety":{"outputDisabled":True,"liveOutput":False,"gpioAccess":False,"clockEnabled":False,"dmaActive":False,"sdrActive":False,"rf":False}}
with tempfile.NamedTemporaryFile(dir=ROOT / "tests/fixtures", suffix=".json", mode="w+") as bootstrap:
    json.dump(bootstrap_value,bootstrap); bootstrap.write("\n"); bootstrap.flush()
    bound=copy.deepcopy(current); bound["schemaVersion"]=3
    source=ROOT/"scripts/gate_d_bootstrap.py"; source_sha=__import__("hashlib").sha256(source.read_bytes()).hexdigest()
    bound["tooling"]["bootstrapExecutor"]={"sourcePath":"scripts/gate_d_bootstrap.py","installedPath":"/usr/libexec/rp1-gpclk-dkms/gate-d-bootstrap","sourceSha256":source_sha,"installedSha256":source_sha,"installKind":"copied","candidateArchiveMember":True}
    bound["qualificationBootstrap"]={
        "path": str(pathlib.Path(bootstrap.name).relative_to(ROOT)),
        "sha256": __import__("hashlib").sha256(pathlib.Path(bootstrap.name).read_bytes()).hexdigest()}
    assert tool.validate(bound)["attemptCount"]==38
    bad=copy.deepcopy(bound); bad["qualificationBootstrap"]["sha256"]="0"*64
    try: tool.validate(bad)
    except ValueError: pass
    else: raise AssertionError("changed bootstrap binding accepted")
for mutation in (
    lambda value: value["tooling"]["bootSelector"].pop("sourceSha256"),
    lambda value: value["tooling"]["bootSelector"].pop("installedSha256"),
    lambda value: value["tooling"]["bootSelector"].update(installKind="target-built"),
    lambda value: value["tooling"]["busyInjector"].update(installKind="copied"),
    lambda value: value["tooling"]["bootSelector"].update(installedSha256="b" * 64),
    lambda value: value["tooling"]["bootSelector"].update(sourceSha256="c" * 64,
                                                               installedSha256="c" * 64),
):
    bad = copy.deepcopy(current)
    mutation(bad)
    try:
        tool.validate(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("split tooling identity mutation accepted")

print("Gate D complete target operation plan: PASS")
