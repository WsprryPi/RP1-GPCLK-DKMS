<!-- SPDX-License-Identifier: MIT -->

# Phase 5.51 attempt 3 prior-kernel downgrade GPIO4 failure review

Status: terminal fail-closed stop at preflight. No lifecycle mutation, boot
selection, or reboot began, and attempt 4 was not started.

The exact installed executor, root marker, schema-6 instance, attempt index,
and third indexed document passed identity validation. Execution created the
attempt evidence directory and completed only `01-create-evidence`.
`02-capture-preflight` then rejected the running normal kernel
`6.18.34+rpt-rpi-2712` because the attempt document declares
`kernelRelease=6.12.75+rpt-rpi-2712`.

This is a deterministic ordering defect in the frozen attempt. The document
places `select-prior-kernel` and `pause-reboot-prior` at steps 7 and 8, after
`capture-preflight` at step 2. The executor requires the declared prior kernel
during that earlier preflight, so the normal-kernel starting state can never
reach the sealed boot-selection steps. Starting manually on the prior kernel
would bypass the document-owned selection, recovery, and original-kernel
provenance contract and is not an acceptable workaround.

The sealed journal is `inactive-recovery-required`. Same-operation `--resume`
is allowed only for an unsealed `reboot-required` journal, which this is not.
No recovery was invoked, the failed evidence was preserved, and the frozen
attempt must not be retried or edited in place.

Independent post-failure checks verified the original `config.txt` and
`tryboot.txt` hashes, the sealed prior-kernel and initramfs hashes, the absence
of test-owned boot artifacts and configuration markers, and the unchanged
boot identity. No reboot occurred. Attempt staging is absent; all six services
remain inactive; and no DKMS test version, module, endpoint, or overlay exists.
Phase 5.51 namespaces contain no forbidden files, extended attributes, links,
or special files.

No GPIO output, active pinctrl, clock enablement, DMA submission, Si5351 or SDR
operation, antenna connection, transmission, or RF occurred. The next gated
work is an offline successor control set that separates the normal-kernel
pre-boot preflight from the prior-kernel post-reboot verification, adds a
regression for their ordering, regenerates all dependent identities, and
receives fresh target authorization. Attempt 4 cannot safely recover this
same-operation failure and was not started.
