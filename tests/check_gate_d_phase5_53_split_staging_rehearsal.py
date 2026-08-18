#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise the complete Phase 5.53 staging transport and archived entry point."""
from __future__ import annotations
import hashlib, importlib.util, json, os, pathlib, subprocess, sys, tarfile, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1];release=os.environ.get('PHASE5_53_RELEASE_DIRECTORY')
if not release:
    print('Phase 5.53 complete split-staging transport: SKIP (release directory not supplied)');raise SystemExit
spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build_phase5_53_staging_transport.py');assert spec and spec.loader
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
def sha(path:pathlib.Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as temporary:
    root=pathlib.Path(temporary);archive=root/'transport.ustar';manifest_path=root/'source-map.json';archive2=root/'transport-2.ustar';manifest2_path=root/'source-map-2.json'
    manifest=builder.build(pathlib.Path(release),archive,manifest_path)
    manifest2=builder.build(pathlib.Path(release),archive2,manifest2_path)
    assert archive.read_bytes()==archive2.read_bytes() and manifest==manifest2
    assert manifest['regularFileCount']==118 and len(manifest['sources'])==118
    assert {x['owner'] for x in manifest['sources']}=={'release-directory','repository-control-set','product-archive-member','separately-sealed-envelope'}
    extracted=root/'extracted';extracted.mkdir()
    with tarfile.open(archive,'r:') as transport:
        members=transport.getmembers();assert sum(x.isfile() for x in members)==118
        assert all(x.isfile() or x.isdir() for x in members) and not any(x.pax_headers for x in members)
        transport.extractall(extracted,filter='data')
    stage=extracted/builder.STAGE;envelope_path=stage/builder.SEALED
    envelope=json.loads(envelope_path.read_text());base='/home/pi/gate-d-inputs/'+builder.STAGE
    executor=pathlib.Path(envelope['stagedExecutor']['path'].replace(base,str(stage)));module=pathlib.Path(envelope['preRootModule']['path'].replace(base,str(stage)))
    assert sha(executor)==envelope['stagedExecutor']['sha256'] and sha(module)==envelope['preRootModule']['sha256']
    rewritten=json.loads(json.dumps(envelope).replace(base,str(stage)).replace('/home/pi/gate-d-qualification/'+builder.STAGE,str(root/'qualification')))
    marker=rewritten['proposedRoot']['marker'];marker['rootPath']=str(root/'qualification');rewritten['proposedRoot']['markerSha256']=hashlib.sha256((json.dumps(marker,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()
    document=root/'rewritten-envelope.json';document.write_text(json.dumps(rewritten,indent=2,sort_keys=True)+'\n')
    result=subprocess.run([sys.executable,str(executor),'pre-root-bootstrap',str(document),'--envelope-sha256',sha(document)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    assert json.loads(result.stdout)=={'outputDisabled':True,'readOnly':True,'valid':True}
print('Phase 5.53 complete 118-file split-staging transport and archived entry point: PASS')
