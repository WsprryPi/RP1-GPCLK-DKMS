#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations
import copy, hashlib, importlib.util, json, os, pathlib, shutil, stat, subprocess, sys, tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("gate_d_root",ROOT/"scripts/gate_d_root.py"); assert spec and spec.loader
tool=importlib.util.module_from_spec(spec); spec.loader.exec_module(tool)

with tempfile.TemporaryDirectory() as temporary:
    base=pathlib.Path(temporary).resolve(); root=base/"qualification"; root.mkdir(mode=0o700)
    marker={"SPDX-License-Identifier":"MIT","schemaVersion":1,"kind":"gate-d-qualification-root-identity","rootPath":str(root),"candidateRelease":"0.0.0-phase5.37","sourceCommit":"1"*40}
    identity=root/".gate-d-root.json"; identity.write_text(json.dumps(marker,sort_keys=True)+"\n"); identity.chmod(0o400)
    reference={"path":str(root),"identityFile":identity.name,"identitySha256":hashlib.sha256(identity.read_bytes()).hexdigest(),"ownerUid":os.getuid(),"mode":"0700"}
    assert tool.validate(reference)==root
    payload=root/"release/input.json"; payload.parent.mkdir(); payload.write_text("{}\n")
    assert tool.resolve(reference,"release/input.json")==payload
    for mutate in (
        lambda value:value.update(path="relative"),
        lambda value:value.update(path=str(base/"missing")),
        lambda value:value.update(identitySha256="0"*64),
        lambda value:value.update(ownerUid=os.getuid()+1),
        lambda value:value.update(mode="0755"),
        lambda value:value.update(identityFile="../marker"),
    ):
        bad=copy.deepcopy(reference); mutate(bad)
        try: tool.validate(bad)
        except ValueError: pass
        else: raise AssertionError("unsafe qualification root accepted")
    try: tool.resolve(reference,"../etc/passwd")
    except ValueError: pass
    else: raise AssertionError("qualification-root traversal accepted")
    link=base/"root-link"; link.symlink_to(root); bad=copy.deepcopy(reference); bad["path"]=str(link)
    try: tool.validate(bad)
    except ValueError: pass
    else: raise AssertionError("symlinked qualification root accepted")
    root.chmod(0o755)
    try: tool.validate(reference)
    except ValueError: pass
    else: raise AssertionError("permission-incompatible qualification root accepted")
    root.chmod(0o700)
    installed=base/"usr/libexec/rp1-gpclk-dkms"; installed.mkdir(parents=True)
    shutil.copy2(ROOT/"scripts/gate_d_root.py",installed/"gate_d_root.py")
    check=subprocess.run([sys.executable,"-c","import gate_d_root, json, sys; gate_d_root.validate(json.loads(sys.argv[1]))",json.dumps(reference)],cwd=base,env={**os.environ,"PYTHONPATH":str(installed)},check=False)
    assert check.returncode==0
print("Gate D qualification root: PASS")
