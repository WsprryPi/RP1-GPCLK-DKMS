#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate and execute the closed output-disabled Gate D bootstrap plan."""
from __future__ import annotations

import hashlib, json, os, pathlib, re, subprocess
from datetime import datetime, timezone
from typing import Callable

SHA = re.compile(r"[0-9a-f]{64}")
COMMIT = re.compile(r"[0-9a-f]{40}")
CHECKPOINTS = ("preflight", "install", "cleanup-runtime", "verify-tools", "empty-runtime-baseline", "commit")

def digest(path: pathlib.Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def real(path: pathlib.Path, label: str) -> None:
    if path.is_symlink() or not path.is_file(): raise ValueError(f"{label} must be a real file")
def atomic(path: pathlib.Path, value: dict) -> None:
    if path.is_symlink(): raise ValueError("bootstrap journal is a symlink")
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("x", encoding="utf-8") as output:
        json.dump(value, output, indent=2, sort_keys=True); output.write("\n"); output.flush(); os.fsync(output.fileno())
    os.replace(temporary, path)

def validate(value: dict, *, root: pathlib.Path = pathlib.Path("/"), verify_files: bool = False) -> dict:
    required={"SPDX-License-Identifier","schemaVersion","kind","operationId","hostId","predecessorVersion","kernelRelease","stagingDirectory","candidate","qualificationIdentity","administrator","argv","cleanupArgv","recoveryArgv","journal","deadlineSeconds","expectedPreState","expectedPostState","retainedTools","cleanupPaths","safety"}
    if set(value)!=required or value.get("SPDX-License-Identifier")!="MIT" or value.get("schemaVersion")!=1 or value.get("kind")!="gate-d-qualification-bootstrap-plan": raise ValueError("invalid bootstrap identity")
    candidate=value["candidate"]
    if set(candidate)!={"release","sourceCommit","archive","archiveSha256"} or not COMMIT.fullmatch(candidate.get("sourceCommit","")) or not SHA.fullmatch(candidate.get("archiveSha256","")): raise ValueError("invalid bootstrap candidate")
    identity=value["qualificationIdentity"]
    admin=value["administrator"]
    if set(identity)!={"path","sha256"} or not SHA.fullmatch(identity.get("sha256","")): raise ValueError("invalid qualification identity")
    if (set(admin)!={"sourcePath","sourceSha256","bootstrapPath","installedPath","installedSha256"} or
            pathlib.PurePosixPath(admin.get("sourcePath", "")).is_absolute() or
            ".." in pathlib.PurePosixPath(admin.get("sourcePath", "")).parts or
            any(not SHA.fullmatch(admin.get(k,"")) for k in ("sourceSha256","installedSha256")) or
            admin["sourceSha256"]!=admin["installedSha256"]): raise ValueError("invalid administrator identity")
    for field in ("predecessorVersion", "kernelRelease"):
        if not isinstance(value[field], str) or not value[field] or any(character.isspace() for character in value[field]): raise ValueError("invalid bootstrap lifecycle identity")
    expected=["/usr/bin/python3",admin["bootstrapPath"],"install","--execute","--release-directory",str(pathlib.PurePosixPath(candidate["archive"]).parent),"--route","gpio4","--qualification-install","--qualification-identity",identity["path"]]
    cleanup=["/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle","dispatch","complete-removal",value["predecessorVersion"],candidate["release"],value["kernelRelease"],value["stagingDirectory"],"--execute"]
    recovery=["/usr/bin/python3",admin["bootstrapPath"],"recover","--execute"]
    if value["argv"]!=expected or value["cleanupArgv"]!=cleanup or value["recoveryArgv"]!=recovery: raise ValueError("bootstrap argv differs")
    baseline={"moduleLoaded":False,"endpointPresent":False,"overlayActive":False,"dkmsTestVersions":False,"liveOutput":False}
    if value["expectedPreState"]!=baseline or value["expectedPostState"]!=baseline or value["safety"]!={"outputDisabled":True,"liveOutput":False,"gpioAccess":False,"clockEnabled":False,"dmaActive":False,"sdrActive":False,"rf":False}: raise ValueError("bootstrap safety differs")
    if not isinstance(value["retainedTools"],list) or not value["retainedTools"] or not isinstance(value["cleanupPaths"],list) or not value["cleanupPaths"] or not 1<=value["deadlineSeconds"]<=1800: raise ValueError("bootstrap lifecycle incomplete")
    for item in value["retainedTools"]:
        if not isinstance(item,dict) or set(item)!={"path","sha256"} or not pathlib.PurePosixPath(item.get("path","")).is_absolute() or not SHA.fullmatch(item.get("sha256","")): raise ValueError("invalid retained tool identity")
    for raw in (candidate["archive"],identity["path"],admin["bootstrapPath"],admin["installedPath"],value["stagingDirectory"],value["journal"],*value["cleanupPaths"]):
        pure=pathlib.PurePosixPath(raw)
        if not pure.is_absolute() or ".." in pure.parts: raise ValueError("unsafe bootstrap path")
    if verify_files:
        for raw,sha,label in ((candidate["archive"],candidate["archiveSha256"],"archive"),(identity["path"],identity["sha256"],"identity"),(admin["sourcePath"],admin["sourceSha256"],"administrator source")):
            path=(root/raw.lstrip("/")) if pathlib.PurePosixPath(raw).is_absolute() else root/raw
            real(path,label)
            if digest(path)!=sha: raise ValueError(f"{label} differs")
    return {"valid":True,"readOnly":True,"outputDisabled":True}

def execute(value: dict, *, root: pathlib.Path, runner: Callable[[list[str]], None], probe: Callable[[], dict], stop_after: str|None=None, recover: bool=False) -> dict:
    validate(value,root=root,verify_files=True)
    journal=root/value["journal"].lstrip("/")
    if journal.exists():
        old=json.loads(journal.read_text())
        if not recover or old.get("status")!="recovery-required": raise ValueError("bootstrap journal already exists")
        runner(value["recoveryArgv"])
    state={"operationId":value["operationId"],"status":"in-progress","checkpoint":"preflight","liveOutput":False}
    atomic(journal,state)
    try:
        if probe()!=value["expectedPreState"]: raise ValueError("bootstrap pre-state differs")
        for checkpoint in CHECKPOINTS[1:]:
            state["checkpoint"]=checkpoint; atomic(journal,state)
            if checkpoint=="install": runner(value["argv"])
            if checkpoint=="cleanup-runtime": runner(value["cleanupArgv"])
            if checkpoint=="verify-tools":
                for item in value["retainedTools"]:
                    path=root/item["path"].lstrip("/"); real(path,"retained tool")
                    if digest(path)!=item["sha256"]: raise ValueError("retained tool differs")
            if checkpoint in {"verify-tools","empty-runtime-baseline"} and probe()!=value["expectedPostState"]: raise ValueError("bootstrap post-state differs")
            if checkpoint=="empty-runtime-baseline":
                for raw in value["cleanupPaths"]:
                    residue=root/raw.lstrip("/")
                    if residue.exists() or residue.is_symlink(): raise ValueError("bootstrap residue remains")
            if stop_after==checkpoint: raise InterruptedError(checkpoint)
        state["status"]="complete"; state["completedAt"]=datetime.now(timezone.utc).isoformat(); atomic(journal,state); return state
    except BaseException as error:
        state.update(status="recovery-required",failure=type(error).__name__); atomic(journal,state); raise

def main() -> None:
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument("plan",type=pathlib.Path); args=parser.parse_args()
    real(args.plan,"bootstrap plan"); print(json.dumps(validate(json.loads(args.plan.read_text())),indent=2,sort_keys=True))
if __name__=="__main__": main()
