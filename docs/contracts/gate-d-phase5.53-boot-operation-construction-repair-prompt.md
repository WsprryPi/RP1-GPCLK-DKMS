<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 boot-operation construction repair prompt

Implement only the offline successor repair for the Phase 5.52 attempt-3
failure sealed at commit `22b5657197b37318b45030ab479335f8c42fcadf`.
The failed executor completed source staging and then passed
`gate-d-boot select` a nonexistent `boot-operation.json`.

Add one deterministic, fail-closed transformation from the sealed prior-kernel
attempt document to the schema-1 boot-operation consumed by `gate_d_boot.py`.
Construct the document during `stage-source`, after both archives have been
safely extracted and before boot selection can run. Bind the normal config and
tryboot paths/hashes, prior stock kernel and initramfs paths/hashes, target
kernel, test-owned firmware filenames, and attempt-owned backup/state paths.
Reject non-prior-kernel rows, inconsistent kernel identities, unsafe staging
paths, or incomplete boot inputs.

Add deterministic tests for the exact mapping and negative cases. Prove the
generated document passes the existing boot selector validator. Do not alter
the frozen Phase 5.52 control set or evidence; generate Phase 5.53 controls;
touch the target; clean up or resume the sealed failure; change boot files;
reboot; administer DKMS, overlays, modules, GPIO, clocks, DMA, I2C, SDR, or RF;
or claim the target blocker resolved. A later gated slice must freeze and
validate a successor release/control set before any target recovery.
