#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independently validate a qualification-only successor release unit."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, pathlib, re, subprocess, tarfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
QLAYOUT=ROOT/"release/qualification-layout-v1.json"; SHA=re.compile(r"([0-9a-f]{64})  ([A-Za-z0-9][A-Za-z0-9._+-]*)")
spec=importlib.util.spec_from_file_location("qualification_successor_validator",ROOT/"scripts/build_qualification_successor.py"); assert spec and spec.loader
builder=importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
def digest(path:pathlib.Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def fail(message:str)->None: raise SystemExit(message)
def validate(frozen:pathlib.Path,successor:pathlib.Path,expected_product_sha256:str)->None:
    frozen_metadata,_=builder.load_frozen(frozen,expected_product_sha256)
    if successor.is_symlink() or not successor.is_dir(): fail("successor must be a real directory")
    frozen_names={p.name for p in frozen.iterdir() if p.is_file() and not p.is_symlink()}; successor_names={p.name for p in successor.iterdir() if p.is_file() and not p.is_symlink()}
    if successor_names!=frozen_names: fail("successor artifact set differs")
    metadata=json.loads((successor/"release-metadata.json").read_text()); provenance=json.loads((successor/"PROVENANCE.json").read_text())
    required={"qualificationSourceCommit","qualificationSourceDateEpoch","qualificationLayoutSha256","qualificationDirtySource"}
    if not required<=metadata.keys() or any(provenance.get(key)!=metadata[key] for key in required): fail("qualification successor identity is incomplete")
    if not re.fullmatch(r"[0-9a-f]{40}",metadata["qualificationSourceCommit"]) or type(metadata["qualificationSourceDateEpoch"]) is not int or metadata["qualificationLayoutSha256"]!=digest(QLAYOUT) or type(metadata["qualificationDirtySource"]) is not bool or metadata.get("publishable") is not False: fail("qualification successor identity differs")
    if metadata.get("sourceCommit")!=frozen_metadata.get("sourceCommit") or metadata.get("archiveSha256")!=expected_product_sha256: fail("retained product identity differs")
    renewed={"release-metadata.json","PROVENANCE.json","SHA256SUMS",metadata["qualificationArchive"]}
    for name in successor_names-renewed:
        if digest(successor/name)!=digest(frozen/name): fail(f"retained product artifact differs: {name}")
    entries={}
    for line in (successor/"SHA256SUMS").read_text().splitlines():
        match=SHA.fullmatch(line)
        if not match or match.group(2) in entries: fail("successor checksums are malformed")
        entries[match.group(2)]=match.group(1)
    if set(entries)!=successor_names-{"SHA256SUMS"} or any(digest(successor/name)!=value for name,value in entries.items()): fail("successor checksum coverage or bytes differ")
    archive=successor/metadata["qualificationArchive"]
    if digest(archive)!=metadata.get("qualificationArchiveSha256"): fail("qualification archive hash differs")
    layout=json.loads(QLAYOUT.read_text()); tracked=subprocess.check_output(["git","-C",str(ROOT),"ls-files","--cached","--others","--exclude-standard","-z"],text=True).split("\0")
    patterns=tuple(item["path"] for item in layout["artifacts"] if item["kind"] in {"archive","archive-tree"}); expected={name for name in tracked if name=="release/qualification-layout-v1.json" or any(pathlib.PurePosixPath(name).match(pattern) for pattern in patterns)}
    prefix=f"{layout['package']}-{layout['release']}/"
    with tarfile.open(archive,"r:gz") as source:
        members=source.getmembers(); names=[member.name.removeprefix(prefix) for member in members]
        if set(names)!=expected or names!=sorted(names) or len(names)!=len(set(names)): fail("qualification archive inventory differs")
        if any(not m.name.startswith(prefix) or not m.isfile() or m.issym() or m.islnk() or m.uid or m.gid or m.uname or m.gname or m.mtime!=metadata["qualificationSourceDateEpoch"] or m.mode not in {0o644,0o755} for m in members): fail("qualification archive metadata differs")
        for member in members:
            rel=member.name.removeprefix(prefix)
            if source.extractfile(member).read()!=(ROOT/rel).read_bytes(): fail(f"qualification archive byte differs: {rel}")
    print("qualification-only successor validation: PASS")
def main()->None:
    parser=argparse.ArgumentParser(); parser.add_argument("frozen",type=pathlib.Path); parser.add_argument("successor",type=pathlib.Path); parser.add_argument("--expected-product-sha256",required=True,choices=["ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549"]); args=parser.parse_args(); validate(args.frozen.resolve(),args.successor.resolve(),args.expected_product_sha256)
if __name__=="__main__": main()
