#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import io
from pathlib import Path
import sys
import tarfile
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import validate_release_candidate as validator

def rejected(callable_):
    try:
        callable_()
    except SystemExit:
        return
    raise AssertionError("invalid candidate input accepted")

def ar_member(name, content):
    header=(f"{name + '/':<16}{0:<12}{0:<6}{0:<6}{100644:<8}{len(content):<10}`\n").encode()
    return header+content+(b"\n" if len(content)%2 else b"")

with tempfile.TemporaryDirectory() as temporary:
    root=Path(temporary)
    package=root/'test.deb'
    package.write_bytes(b"!<arch>\n"+ar_member('debian-binary',b'2.0\n')+
        ar_member('control.tar.xz',b'control')+ar_member('data.tar.xz',b'data'))
    assert set(validator.ar_members(package))=={'debian-binary','control.tar.xz','data.tar.xz'}
    bad=bytearray(package.read_bytes()); bad[0]=0
    (root/'bad.deb').write_bytes(bad)
    rejected(lambda: validator.ar_members(root/'bad.deb'))

    payload=io.BytesIO()
    with tarfile.open(fileobj=payload,mode='w:xz') as archive:
        member=tarfile.TarInfo('safe/file'); content=b'bytes\n'
        member.size=len(content); member.mode=0o644
        archive.addfile(member,io.BytesIO(content))
    records, files=validator.tar_inventory(payload.getvalue())
    assert records[0]['path']=='safe/file' and files['safe/file']==b'bytes\n'

    unsafe=io.BytesIO()
    with tarfile.open(fileobj=unsafe,mode='w:xz') as archive:
        member=tarfile.TarInfo('../escape'); member.size=1
        archive.addfile(member,io.BytesIO(b'x'))
    rejected(lambda: validator.tar_inventory(unsafe.getvalue()))

    candidate=root/'candidate'; candidate.mkdir()
    for name in validator.FILES:
        (candidate/name).write_bytes(b'')
    (candidate/'extra').write_bytes(b'x')
    rejected(lambda: validator.validate(candidate,None))
    (candidate/'extra').unlink()
    (candidate/'SHA256SUMS').write_text('0'*64+'  unknown\n')
    rejected(lambda: validator.validate(candidate,None))

source=(ROOT/'scripts/validate_release_candidate.py').read_text()
for token in (
    'candidate set differs', 'checksum coverage or ordering differs',
    'Debian member inventory differs', 'qualification content leaked',
    'source commit differs from expectation',
    'candidate compatibility is not fully fail-closed',
    'qualification archive member inventory differs',
    'qualification sidecar byte mismatch',
):
    assert token in source, token
legacy=(ROOT/'scripts/validate_release.py').read_text()
assert 'release/release-layout-v1.json' in legacy
assert 'validate_release_candidate' not in legacy
make=(ROOT/'Makefile').read_text()
assert 'validate-release-candidate:' in make
layout=(ROOT/'release/qualification-layout-v3.json').read_text()
assert 'scripts/validate_release_candidate.py' in layout
print('Release candidate validator: PASS (strict primitives and negative cases)')
