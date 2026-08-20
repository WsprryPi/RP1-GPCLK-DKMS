<!-- SPDX-License-Identifier: MIT -->

# Phase 5.46 lifecycle attempt 1 failure review

Status: terminal fail-closed stop at preflight. No lifecycle mutation began,
and attempt 2 was not started.

The exact installed executor, root marker, authorized instance, attempt index,
and entry-1 document passed preflight identity validation. Execution created
the attempt evidence directory and completed only `01-create-evidence`.
`02-capture-preflight` then failed before its first state-changing operation:
the controlled-path resolver rejected `/proc/device-tree/rp1-gpclk` because
the standard `/proc/device-tree` path is itself a symlink to the kernel's
device-tree view.

The failure is deterministic in the frozen executor. Its `rooted()` helper
rejects any symlink component before testing whether the optional resource node
exists. Therefore a normal Raspberry Pi `/proc/device-tree` layout cannot pass
this preflight, even when `rp1-gpclk` is absent. This is an executor path-model
defect, not evidence of a resource conflict or unsafe target state.

The sealed journal is `inactive-recovery-required`, but same-operation recovery
is not authorized or implementable: the executor accepts `--resume` only for
unsealed reboot-required journals and requires a different operation identity
for `--recover-from`. The Phase 5.46 index contains no recovery operation for
this unexpected preflight failure. No recovery was invoked; the sealed evidence
was preserved.

Post-failure checks confirm no DKMS, service, overlay, module, endpoint, GPIO,
clock, DMA, I2C, Si5351, SDR, antenna, transmission, or RF operation began. All
six services remain inactive, the module and endpoint are absent, no overlay or
Phase 5.46 DKMS test version exists, and output remained disabled.

The current attempt and control set must not be retried. The next gated work is
an offline successor that makes the device-tree resource check resolve the
canonical kernel device-tree path safely, adds regression coverage for the
standard `/proc/device-tree` symlink and malicious descendant symlinks, freezes
a new candidate, and rebuilds and revalidates before any new authorization.
