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
def validate_package_paths(items: object) -> list[dict]:
    if not isinstance(items,list) or not items: raise ValueError("typed package inventory is empty")
    paths=[]
    for item in items:
        common={"path","type","mode","ownerUid","groupGid"}
        if (not isinstance(item,dict) or item.get("type") not in {"file","symlink"} or
                not pathlib.PurePosixPath(item.get("path","")).is_absolute() or
                ".." in pathlib.PurePosixPath(item["path"]).parts or
                item.get("mode") not in {"0644","0755","0777"} or
                type(item.get("ownerUid")) is not int or item["ownerUid"]<0 or
                type(item.get("groupGid")) is not int or item["groupGid"]<0):
            raise ValueError("invalid typed package identity")
        if item["type"]=="file":
            if set(item)!=common|{"sha256"} or not SHA.fullmatch(item.get("sha256","")) or item["mode"] not in {"0644","0755"}: raise ValueError("invalid typed package file")
        elif (set(item)!=common|{"target"} or not isinstance(item.get("target"),str) or
              not item["target"] or pathlib.PurePosixPath(item["target"]).is_absolute() or item["mode"] not in {"0755","0777"}): raise ValueError("invalid typed package symlink")
        paths.append(item["path"])
    if len(paths)!=len(set(paths)): raise ValueError("duplicate typed package path")
    return items
def package_paths_digest(items:list[dict])->str:
    return hashlib.sha256((json.dumps(items,sort_keys=True,separators=(",",":"))+"\n").encode()).hexdigest()
def verify_package_path(root:pathlib.Path,item:dict)->None:
    path=root/item["path"].lstrip("/"); status=path.lstat()
    if status.st_uid!=item["ownerUid"] or status.st_gid!=item["groupGid"] or (status.st_mode & 0o777)!=int(item["mode"],8): raise ValueError("typed package metadata differs")
    if item["type"]=="file":
        if path.is_symlink() or not path.is_file() or digest(path)!=item["sha256"]: raise ValueError("typed package file differs")
    elif not path.is_symlink() or os.readlink(path)!=item["target"]: raise ValueError("typed package symlink differs")
def atomic(path: pathlib.Path, value: dict) -> None:
    if path.is_symlink(): raise ValueError("bootstrap journal is a symlink")
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("x", encoding="utf-8") as output:
        json.dump(value, output, indent=2, sort_keys=True); output.write("\n"); output.flush(); os.fsync(output.fileno())
    os.replace(temporary, path)

def validate(value: dict, *, root: pathlib.Path = pathlib.Path("/"), verify_files: bool = False) -> dict:
    required={"SPDX-License-Identifier","schemaVersion","kind","operationId","hostId","predecessorVersion","kernelRelease","stagingDirectory","candidate","qualificationIdentity","administrator","argv","cleanupArgv","recoveryArgv","journal","deadlineSeconds","expectedPreState","expectedPostState","retainedTools","cleanupPaths","safety"}
    schema=value.get("schemaVersion")
    if schema in {2,3,4}: required.add("qualificationRoot")
    if schema==4: required.update({"packagePaths","packagePathsSha256"})
    if set(value)!=required or value.get("SPDX-License-Identifier")!="MIT" or schema not in {1,2,3,4} or value.get("kind")!="gate-d-qualification-bootstrap-plan": raise ValueError("invalid bootstrap identity")
    if schema in {2,3,4}:
        import sys
        scripts=pathlib.Path(__file__).resolve().parent
        if str(scripts) not in sys.path: sys.path.insert(0,str(scripts))
        from gate_d_root import validate as validate_root
        validate_root(value["qualificationRoot"])
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
    baseline={"moduleLoaded":False,"endpointPresent":False,"overlayActive":False,"dkmsTestVersions":False,"outputActive":False}
    if value["expectedPreState"]!=baseline or value["expectedPostState"]!=baseline or value["safety"]!={"outputDisabled":True,"outputActive":False,"gpioAccess":False,"clockEnabled":False,"dmaActive":False,"sdrActive":False,"rf":False}: raise ValueError("bootstrap safety differs")
    if not isinstance(value["retainedTools"],list) or not value["retainedTools"] or not isinstance(value["cleanupPaths"],list) or not value["cleanupPaths"] or not 1<=value["deadlineSeconds"]<=1800: raise ValueError("bootstrap lifecycle incomplete")
    for item in value["retainedTools"]:
        if not isinstance(item,dict) or set(item)!={"path","sha256"} or not pathlib.PurePosixPath(item.get("path","")).is_absolute() or not SHA.fullmatch(item.get("sha256","")): raise ValueError("invalid retained tool identity")
    if schema in {2,3,4} and [item["path"] for item in value["retainedTools"]].count("/usr/libexec/rp1-gpclk-dkms/gate_d_root.py")!=1:
        raise ValueError("bootstrap root-validator retained identity is absent")
    if schema in {3,4}:
        required_modules={
            "/usr/libexec/rp1-gpclk-dkms/gate_d_root.py",
            "/usr/libexec/rp1-gpclk-dkms/gate_d_bootstrap.py",
            "/usr/libexec/rp1-gpclk-dkms/gate_d_target_plan.py",
            "/usr/libexec/rp1-gpclk-dkms/gate_d_lifecycle.py",
            "/usr/libexec/rp1-gpclk-dkms/gate_d_outer.py",
            "/usr/libexec/rp1-gpclk-dkms/gate_d_attempts.py",
            "/usr/libexec/rp1-gpclk-dkms/gate_d_instance.py",
            "/usr/libexec/rp1-gpclk-dkms/gate_d_preroot.py",
        }
        retained_paths=[item["path"] for item in value["retainedTools"]]
        if not required_modules.issubset(retained_paths) or len(retained_paths)!=len(set(retained_paths)):
            raise ValueError("bootstrap retained Python import graph is incomplete")
    if schema==4:
        package_paths=validate_package_paths(value["packagePaths"])
        if not SHA.fullmatch(value.get("packagePathsSha256","")) or package_paths_digest(package_paths)!=value["packagePathsSha256"]: raise ValueError("typed package inventory digest differs")
        package_names={item["path"] for item in package_paths}
        retained_names={item["path"] for item in value["retainedTools"]}
        if not retained_names.issubset(package_names): raise ValueError("retained tools are outside typed package inventory")
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
    state={"operationId":value["operationId"],"status":"in-progress","checkpoint":"preflight","outputActive":False}
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
                if value["schemaVersion"]==4:
                    for item in value["packagePaths"]: verify_package_path(root,item)
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
