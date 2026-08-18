#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the complete Phase 5.53 staging ustar from explicit artifact owners."""
from __future__ import annotations
import argparse, hashlib, io, json, pathlib, tarfile, tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
STAGE='phase5.53-1884c0f1c53c';PREFIX=f'/home/pi/gate-d-inputs/{STAGE}/'
ENVELOPE=ROOT/'release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json'
PRODUCT='rp1-gpclk-dkms-0.0.0-phase5.53.tar.gz';PRODUCT_ROOT='rp1-gpclk-dkms-0.0.0-phase5.53'
SEALED='gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json'
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def build(release_dir:pathlib.Path,output:pathlib.Path,manifest_path:pathlib.Path)->dict:
    if output.exists() or manifest_path.exists():raise ValueError('output already exists')
    envelope=json.loads(ENVELOPE.read_text());declared={x['path']:x['sha256'] for x in envelope['inputFiles']}
    release_paths={x['path'] for x in envelope['releaseInputs']};transition_paths={x['sourcePath'] for x in envelope['transitionFiles']};administrator=envelope['administrator']['path']
    if len(declared)!=64 or len(release_paths)!=8 or len(transition_paths)!=55:raise ValueError('input graph differs')
    if set(declared)!=release_paths|transition_paths|{administrator}:raise ValueError('input ownership graph is incomplete')
    with tempfile.TemporaryDirectory() as temporary:
        tree=pathlib.Path(temporary);stage=tree/STAGE;stage.mkdir();owners=[]
        for raw,expected in sorted(declared.items()):
            if not raw.startswith(PREFIX):raise ValueError('input outside staging root')
            rel=raw.removeprefix(PREFIX);dest=stage/rel
            if raw==administrator:continue
            if raw in release_paths:source=release_dir/pathlib.PurePosixPath(raw).name;owner='release-directory';source_id='release-directory/'+source.name
            elif raw in transition_paths:source=ROOT/rel.removeprefix('control-set/');owner='repository-control-set';source_id='repository/'+rel.removeprefix('control-set/')
            else:raise ValueError(f'unowned input: {raw}')
            if source.is_symlink() or not source.is_file():raise ValueError(f'missing owned input: {source}')
            payload=source.read_bytes()
            if sha(payload)!=expected:raise ValueError(f'owned input hash differs: {raw}')
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(payload);owners.append({'path':raw,'owner':owner,'source':source_id,'sha256':expected})
        archive_path=stage/PRODUCT
        with tarfile.open(archive_path,'r:gz') as archive:
            members=archive.getmembers();names=[m.name.rstrip('/') for m in members]
            if len(names)!=len(set(names)) or any(not(m.isdir() or m.isfile()) for m in members):raise ValueError('product archive type graph differs')
            files=[m for m in members if m.isfile()]
            if len(files)!=54:raise ValueError('product archive file count differs')
            for member in members:
                pure=pathlib.PurePosixPath(member.name)
                if pure.is_absolute() or '..' in pure.parts or not pure.parts or pure.parts[0]!=PRODUCT_ROOT:raise ValueError('unsafe product archive member')
                dest=stage/'extracted'/pure
                if member.isdir():dest.mkdir(parents=True,exist_ok=True);continue
                source=archive.extractfile(member)
                if source is None:raise ValueError('unreadable product member')
                payload=source.read();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(payload);raw=PREFIX+'extracted/'+pure.as_posix();owners.append({'path':raw,'owner':'product-archive-member','source':PRODUCT+':'+pure.as_posix(),'sha256':sha(payload)})
        for raw,expected in declared.items():
            path=tree/raw.removeprefix('/home/pi/gate-d-inputs/')
            if path.is_symlink() or not path.is_file() or sha(path.read_bytes())!=expected:raise ValueError(f'materialized input differs: {raw}')
        sealed=stage/SEALED;sealed.write_bytes(ENVELOPE.read_bytes());owners.append({'path':PREFIX+SEALED,'owner':'separately-sealed-envelope','source':'repository/release/'+ENVELOPE.name,'sha256':sha(sealed.read_bytes())})
        files=sorted(p for p in tree.rglob('*') if p.is_file());dirs=sorted([tree,*(p for p in tree.rglob('*') if p.is_dir())],key=lambda p:p.relative_to(tree).as_posix())
        if len(files)!=118 or len({x['path'] for x in owners})!=118:raise ValueError('complete staging closure differs')
        with tarfile.open(output,'w',format=tarfile.USTAR_FORMAT) as archive:
            for directory in dirs:
                rel=directory.relative_to(tree);name=STAGE if rel==pathlib.Path('.') else rel.as_posix();info=tarfile.TarInfo(name.rstrip('/')+'/');info.type=tarfile.DIRTYPE;info.mode=0o700;info.uid=info.gid=1000;info.uname=info.gname='pi';info.mtime=0;archive.addfile(info)
            for path in files:
                payload=path.read_bytes();info=tarfile.TarInfo(path.relative_to(tree).as_posix());info.size=len(payload);info.mode=0o600;info.uid=info.gid=1000;info.uname=info.gname='pi';info.mtime=0;archive.addfile(info,io.BytesIO(payload))
        result={'SPDX-License-Identifier':'MIT','schemaVersion':1,'kind':'gate-d-phase5.53-staging-source-map','transportSha256':sha(output.read_bytes()),'regularFileCount':118,'directoryCountIncludingRoot':len(dirs),'sources':sorted(owners,key=lambda x:x['path'])}
        manifest_path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');return result

def main()->None:
    p=argparse.ArgumentParser();p.add_argument('--release-directory',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--manifest',type=pathlib.Path,required=True);a=p.parse_args();print(json.dumps(build(a.release_directory,a.output,a.manifest),sort_keys=True))
if __name__=='__main__':main()
