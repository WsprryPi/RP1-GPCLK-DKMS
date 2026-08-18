#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise the repaired Phase 5.53 split-staging executor path offline."""
from __future__ import annotations
import hashlib, json, pathlib, subprocess, sys, tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
COMMIT='834d05c5c5da0c383c4a229eaeff9dae07a4359b'
PRODUCT='1884c0f1c53c661495576bf10ce08d8bf7a90bc3'
STAGE='/home/pi/gate-d-inputs/phase5.53-1884c0f1c53c'
PRODUCT_PREFIX='rp1-gpclk-dkms-0.0.0-phase5.53/'

def git_bytes(commit:str,path:str)->bytes:
    return subprocess.check_output(['git','show',f'{commit}:{path}'],cwd=ROOT)
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()

envelope=json.loads((ROOT/'release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json').read_text())
inputs={item['path']:item['sha256'] for item in envelope['inputFiles']}
assert len(inputs)==64
for field in ('stagedExecutor','preRootModule','administrator','qualificationIdentity'):
    item=envelope[field]; assert inputs[item['path']]==item['sha256']
assert envelope['stagedExecutor']['path']==STAGE+'/control-set/scripts/gate_d_outer.py'
assert envelope['preRootModule']['path']==STAGE+'/control-set/scripts/gate_d_preroot.py'
assert envelope['administrator']['path']==STAGE+'/extracted/'+PRODUCT_PREFIX+'scripts/rp1-gpclk-admin.py'

# Reconstruct the exact split path closure: 64 declared inputs, 54 product
# members with one administrator overlap, plus the separately sealed envelope.
layout=json.loads(git_bytes(PRODUCT,'release/release-layout-v1.json'))
tracked=subprocess.check_output(['git','ls-tree','-r','--name-only',PRODUCT],cwd=ROOT,text=True).splitlines()
exact={'Kbuild','LICENSE.md','Makefile','README.md','SECURITY.md','dkms.conf',
       'release/release-layout-v1.json','uapi-identity.json','scripts/build_release.py',
       'scripts/validate_release.py'}
patterns=('LICENSES/*',)+tuple(item['path'] for item in layout['artifacts']
                              if item['kind'] in {'archive','archive-tree'})
product_files=sorted(path for path in tracked if path in exact or
                     any(pathlib.PurePosixPath(path).match(pattern) for pattern in patterns))
assert len(product_files)==54
archive_paths={STAGE+'/extracted/'+PRODUCT_PREFIX+path for path in product_files}
closure=set(inputs)|archive_paths|{STAGE+'/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json'}
assert len(closure)==118
assert envelope['stagedExecutor']['path'] in closure
assert envelope['preRootModule']['path'] in closure

with tempfile.TemporaryDirectory() as temporary:
    root=pathlib.Path(temporary); stage=root/'stage'; qualification=root/'qualification'
    executor=stage/'control-set/scripts/gate_d_outer.py'
    module=stage/'control-set/scripts/gate_d_preroot.py'
    executor.parent.mkdir(parents=True)
    executor.write_bytes(git_bytes(COMMIT,'scripts/gate_d_outer.py'))
    module.write_bytes(git_bytes(COMMIT,'scripts/gate_d_preroot.py'))
    assert sha(executor.read_bytes())==envelope['stagedExecutor']['sha256']
    assert sha(module.read_bytes())==envelope['preRootModule']['sha256']
    rewritten=json.loads(json.dumps(envelope).replace(STAGE,str(stage)).replace(
        '/home/pi/gate-d-qualification/phase5.53-1884c0f1c53c',str(qualification)))
    marker=rewritten['proposedRoot']['marker']; marker['rootPath']=str(qualification)
    rewritten['proposedRoot']['markerSha256']=sha((json.dumps(marker,sort_keys=True,separators=(',',':'))+'\n').encode())
    document=stage/'gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json'
    document.write_text(json.dumps(rewritten,indent=2,sort_keys=True)+'\n')
    result=subprocess.run([sys.executable,str(executor),'pre-root-bootstrap',str(document),
        '--envelope-sha256',sha(document.read_bytes())],cwd=ROOT,text=True,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    assert json.loads(result.stdout)=={'outputDisabled':True,'readOnly':True,'valid':True}
print('Phase 5.53 exact split-staging path closure and archived entry point: PASS')
