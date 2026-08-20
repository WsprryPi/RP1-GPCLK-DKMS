#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate and resolve the sealed Gate D qualification root."""
from __future__ import annotations

import hashlib, json, os, pathlib, re, stat

SHA = re.compile(r"[0-9a-f]{64}")
COMMIT = re.compile(r"[0-9a-f]{40}")

def digest(path: pathlib.Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def _no_symlink_components(path: pathlib.Path) -> None:
    current=pathlib.Path(path.anchor)
    for part in path.parts[1:]:
        current=current/part
        if current.exists() and current.is_symlink(): raise ValueError("qualification root contains a symlink component")

def validate(reference: dict, *, verify: bool=True) -> pathlib.Path:
    fields={"path","identityFile","identitySha256","ownerUid","mode"}
    if not isinstance(reference,dict) or set(reference)!=fields: raise ValueError("qualification-root reference is incomplete")
    raw=reference.get("path"); identity=reference.get("identityFile")
    if not isinstance(raw,str) or not pathlib.PurePosixPath(raw).is_absolute() or raw in {"/","/usr","/var","/home"} or ".." in pathlib.PurePosixPath(raw).parts: raise ValueError("unsafe qualification-root path")
    if not isinstance(identity,str) or pathlib.PurePosixPath(identity).is_absolute() or pathlib.PurePosixPath(identity).name!=identity or identity in {".",".."}: raise ValueError("unsafe qualification-root identity file")
    if not SHA.fullmatch(reference.get("identitySha256","")) or type(reference.get("ownerUid")) is not int or reference.get("ownerUid")<0 or reference.get("mode")!="0700": raise ValueError("invalid qualification-root identity")
    root=pathlib.Path(raw)
    if verify:
        _no_symlink_components(root)
        if root.is_symlink() or not root.is_dir(): raise ValueError("qualification root must be a real directory")
        metadata=root.stat()
        if metadata.st_uid!=reference["ownerUid"] or stat.S_IMODE(metadata.st_mode)!=0o700: raise ValueError("qualification-root ownership or mode differs")
        marker=root/identity
        if marker.is_symlink() or not marker.is_file() or digest(marker)!=reference["identitySha256"]: raise ValueError("qualification-root marker differs")
        value=json.loads(marker.read_text(encoding="utf-8"))
        if (not isinstance(value,dict) or set(value)!={"SPDX-License-Identifier","schemaVersion","kind","rootPath","candidateRelease","sourceCommit"} or value.get("SPDX-License-Identifier")!="MIT" or value.get("schemaVersion")!=1 or value.get("kind")!="gate-d-qualification-root-identity" or value.get("rootPath")!=raw or not isinstance(value.get("candidateRelease"),str) or not COMMIT.fullmatch(value.get("sourceCommit",""))): raise ValueError("qualification-root marker identity is invalid")
    return root

def resolve(reference: dict, relative: str, *, require_file: bool=True) -> pathlib.Path:
    root=validate(reference)
    pure=pathlib.PurePosixPath(relative)
    if not isinstance(relative,str) or pure.is_absolute() or not pure.parts or ".." in pure.parts: raise ValueError("unsafe qualification-root relative path")
    path=root.joinpath(*pure.parts)
    _no_symlink_components(path)
    if require_file and (path.is_symlink() or not path.is_file()): raise ValueError("qualification-root file is absent")
    return path
