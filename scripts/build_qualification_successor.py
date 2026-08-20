#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build an unpublished qualification-only successor release unit."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, pathlib, re, shutil, subprocess

ROOT=pathlib.Path(__file__).resolve().parents[1]
LAYOUT_PATH=ROOT/"release/release-layout-v1.json"; QUALIFICATION_LAYOUT_PATH=ROOT/"release/qualification-layout-v1.json"
SHA=re.compile(r"([0-9a-f]{64})  ([A-Za-z0-9][A-Za-z0-9._+-]*)")
spec=importlib.util.spec_from_file_location("qualification_successor_build",ROOT/"scripts/build_release.py"); assert spec and spec.loader
build=importlib.util.module_from_spec(spec); spec.loader.exec_module(build)
def run(*args:str)->str: return subprocess.check_output(args,cwd=ROOT,text=True).strip()
def digest(path:pathlib.Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()

def load_frozen(directory:pathlib.Path,expected_product_sha256:str)->tuple[dict,dict]:
    if directory.is_symlink() or not directory.is_dir(): raise SystemExit("frozen release unit must be a real directory")
    paths=[directory/name for name in ("release-metadata.json","PROVENANCE.json","SHA256SUMS")]
    if any(path.is_symlink() or not path.is_file() for path in paths): raise SystemExit("frozen release identity sidecar is absent or unsafe")
    metadata=json.loads(paths[0].read_text()); provenance=json.loads(paths[1].read_text()); archive=directory/metadata.get("archive","")
    if metadata.get("archiveSha256")!=expected_product_sha256 or archive.is_symlink() or not archive.is_file() or digest(archive)!=expected_product_sha256: raise SystemExit("frozen product archive bytes differ")
    entries={}
    for line in paths[2].read_text().splitlines():
        match=SHA.fullmatch(line)
        if not match or match.group(2) in entries: raise SystemExit("frozen checksum manifest is malformed")
        entries[match.group(2)]=match.group(1)
    actual={path.name for path in directory.iterdir() if path.is_file() and not path.is_symlink()}
    if set(entries)!=actual-{"SHA256SUMS"} or any(digest(directory/name)!=value for name,value in entries.items()): raise SystemExit("frozen checksum coverage or bytes differ")
    for key in ("archive","archiveSha256","sourceCommit","release","expectedTag"):
        if provenance.get(key)!=metadata.get(key): raise SystemExit(f"frozen provenance differs at {key}")
    return metadata,provenance

def generate(frozen:pathlib.Path,output:pathlib.Path,expected_product_sha256:str,development:bool)->None:
    layout=json.loads(LAYOUT_PATH.read_text()); qualification_layout=json.loads(QUALIFICATION_LAYOUT_PATH.read_text()); metadata,provenance=load_frozen(frozen,expected_product_sha256)
    if metadata.get("release")!=layout.get("release") or qualification_layout.get("release")!=layout.get("release"): raise SystemExit("frozen and successor release identities differ")
    dirty=bool(run("git","status","--porcelain","--untracked-files=all"))
    if dirty and not development: raise SystemExit("refusing qualification successor from a dirty worktree")
    if output.exists():
        if output.is_symlink() or not output.is_dir() or any(output.iterdir()): raise SystemExit("output must be a new or empty real directory")
    else: output.mkdir(parents=True,mode=0o755)
    qualification_files,selected_dirty=build.selected_files(development,qualification_layout,build.QUALIFICATION_RELEASE_EXACT,())
    if selected_dirty!=dirty: raise SystemExit("qualification source state differs")
    commit=run("git","rev-parse","HEAD"); epoch=int(run("git","show","-s","--format=%ct","HEAD")); renewed={"release-metadata.json","PROVENANCE.json","SHA256SUMS",metadata["qualificationArchive"]}; copied={}
    try:
        for source in frozen.iterdir():
            if source.name in renewed: continue
            if source.is_symlink() or not source.is_file(): raise SystemExit(f"unsafe frozen artifact: {source.name}")
            shutil.copyfile(source,output/source.name); copied[source.name]=digest(source)
        qualification_name=f"{qualification_layout['package']}-{layout['release']}.tar.gz"; qualification_archive=output/qualification_name
        build.create_archive(qualification_archive,qualification_files,f"{qualification_layout['package']}-{layout['release']}",epoch)
        successor=dict(metadata); successor.update({"qualificationArchive":qualification_name,"qualificationArchiveSha256":digest(qualification_archive),"qualificationSourceCommit":commit,"qualificationSourceDateEpoch":epoch,"qualificationLayoutSha256":digest(QUALIFICATION_LAYOUT_PATH),"qualificationDirtySource":dirty,"tagPresent":False,"publishable":False})
        build.json_write(output/"release-metadata.json",successor); renewed_provenance=dict(provenance); renewed_provenance.update(successor); renewed_provenance.update({"generationCommand":"scripts/build_qualification_successor.py FROZEN OUTPUT --expected-product-sha256 SHA256 [--development]","qualificationSourceFiles":[path.as_posix() for path in qualification_files],"retainedProductArtifacts":copied}); build.json_write(output/"PROVENANCE.json",renewed_provenance)
        artifacts=sorted(path for path in output.iterdir() if path.name!="SHA256SUMS"); (output/"SHA256SUMS").write_text("".join(f"{digest(path)}  {path.name}\n" for path in artifacts))
        if any(digest(output/name)!=value for name,value in copied.items()): raise SystemExit("copied product artifact bytes changed")
    except BaseException:
        for child in output.iterdir():
            if child.is_file() and not child.is_symlink(): child.unlink()
        raise

def main()->None:
    parser=argparse.ArgumentParser(); parser.add_argument("frozen",type=pathlib.Path); parser.add_argument("output",type=pathlib.Path); parser.add_argument("--expected-product-sha256",required=True,choices=["032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76"]); parser.add_argument("--development",action="store_true")
    args=parser.parse_args(); generate(args.frozen.resolve(),args.output.resolve(),args.expected_product_sha256,args.development)
if __name__=="__main__": main()
