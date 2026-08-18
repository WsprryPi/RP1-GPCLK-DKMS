#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise deterministic qualification-only successor construction."""
import hashlib, importlib.util, json, pathlib, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("qualification_successor",ROOT/"scripts/build_qualification_successor.py"); assert spec and spec.loader
tool=importlib.util.module_from_spec(spec); spec.loader.exec_module(tool)
def sha(path:pathlib.Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as temporary:
    root=pathlib.Path(temporary); frozen=root/"frozen"; first=root/"first"; second=root/"second"; frozen.mkdir()
    product=frozen/"rp1-gpclk-dkms-0.0.0-phase5.53.tar.gz"; product.write_bytes(b"frozen product bytes\n")
    oldq=frozen/"rp1-gpclk-dkms-qualification-0.0.0-phase5.53.tar.gz"; oldq.write_bytes(b"old qualification\n")
    for name in ("rp1-gpclk-gpio4.dtbo","rp1-gpclk-gpio20.dtbo","rp1-gpclk-compatibility-manifest.json"): (frozen/name).write_bytes((name+"\n").encode())
    metadata={"SPDX-License-Identifier":"MIT","schemaVersion":1,"release":"0.0.0-phase5.53","expectedTag":"v0.0.0-phase5.53","sourceCommit":"1"*40,"archive":product.name,"archiveSha256":sha(product),"qualificationArchive":oldq.name,"qualificationArchiveSha256":sha(oldq),"tagPresent":False,"dirtySource":False,"publishable":False}
    provenance=dict(metadata); provenance["sourceFiles"]=[]; provenance["qualificationSourceFiles"]=[]
    (frozen/"release-metadata.json").write_text(json.dumps(metadata)+"\n"); (frozen/"PROVENANCE.json").write_text(json.dumps(provenance)+"\n")
    artifacts=sorted(path for path in frozen.iterdir()); (frozen/"SHA256SUMS").write_text("".join(f"{sha(path)}  {path.name}\n" for path in artifacts))
    tool.generate(frozen,first,sha(product),True); tool.generate(frozen,second,sha(product),True)
    assert {path.name:sha(path) for path in first.iterdir()}=={path.name:sha(path) for path in second.iterdir()}
    assert sha(first/product.name)==sha(product)
    value=json.loads((first/"release-metadata.json").read_text()); assert value["sourceCommit"]=="1"*40 and value["qualificationSourceCommit"]!=value["sourceCommit"] and value["qualificationDirtySource"] is True and value["publishable"] is False
    (frozen/"SHA256SUMS").write_text("0"*64+f"  {product.name}\n")
    try: tool.load_frozen(frozen,sha(product))
    except SystemExit: pass
    else: raise AssertionError("corrupted frozen checksum accepted")
print("qualification-only successor construction: PASS")
