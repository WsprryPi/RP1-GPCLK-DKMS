#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate deterministic successor boot-operation construction."""
import copy
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);assert spec and spec.loader
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module
 spec.loader.exec_module(module);return module
outer=load('gate_d_outer_boot_repair',ROOT/'scripts/gate_d_outer.py')
boot_tool=load('gate_d_boot_repair',ROOT/'scripts/gate_d_boot.py')
attempt=json.loads((ROOT/'release/gate-d-attempts-phase5.52-v1/gd-prior-supported-kernel-downgrade-gpio4.json').read_text())
value=outer.build_boot_operation(attempt)
staging=attempt['inputs']['stagingDirectory'];prior='6.12.75+rpt-rpi-2712'
assert value=={
 'schemaVersion':1,'operationId':'gd-prior-supported-kernel-downgrade-gpio4-boot','targetKernel':prior,
 'sourceKernel':'/boot/vmlinuz-6.12.75+rpt-rpi-2712','sourceKernelSha256':'c194093a665071826ff94fb014b574de8ad896584b7317bbeafefe94154b0b44',
 'sourceInitramfs':'/boot/initrd.img-6.12.75+rpt-rpi-2712','sourceInitramfsSha256':'e3d47bcb88e0a0ed9cb338832fc1ac503d423692ab49842134c68677dc505068',
 'config':'/boot/firmware/config.txt','configSha256':'b6218fd92bd231151f177029b0dfd84a2af1e92f94dac768bd9501af087d43e2',
 'tryboot':'/boot/firmware/tryboot.txt','trybootSha256':'c06b262332c145a0cfea594e020fced762a02eef269e4026fe84de71fb152b0a',
 'stagedKernel':'/boot/firmware/gate-d-stock-6.12.75-rpt-rpi-2712.img','stagedInitramfs':'/boot/firmware/gate-d-stock-6.12.75-rpt-rpi-2712-initramfs',
 'backupConfig':f'{staging}/config.txt.original','state':f'{staging}/boot-state.json'}
assert boot_tool.plan(value)['targetKernel']==prior
with tempfile.TemporaryDirectory() as temporary:
 staged_attempt=copy.deepcopy(attempt)
 staged_attempt['inputs']['stagingDirectory']='/staging'
 original_extract=outer.safe_extract
 outer.safe_extract=lambda archive,destination:destination.mkdir(parents=True)
 try:outer.default_internal('stage-source',staged_attempt,Path(temporary))
 finally:outer.safe_extract=original_extract
 generated=Path(temporary)/'staging/boot-operation.json'
 assert generated.is_file() and boot_tool.load(generated)==outer.build_boot_operation(staged_attempt)
for mutate in (
 lambda x:x.update(matrixRow='current-supported-kernel'),
 lambda x:x.update(kernelRelease='6.18.34+rpt-rpi-2712'),
 lambda x:x['inputs'].update(stagingDirectory='../unsafe'),
 lambda x:x['inputs']['boot'].pop('priorInitramfsSha256')):
 candidate=copy.deepcopy(attempt);mutate(candidate)
 try:outer.build_boot_operation(candidate)
 except ValueError:pass
 else:raise AssertionError('unsafe boot-operation input accepted')
print('Gate D successor boot-operation construction: PASS')
