<!-- SPDX-License-Identifier: MIT -->

# Phase 5.48 attempt 1 authenticated residue-cleanup prompt

Clean only the terminal attempt-owned residue identified by commit
`26924c0e5111b5a301a12c3480a665edaca18cbd` after Phase 5.48 attempt 1.
Bind this cleanup to operation `gd-current-supported-kernel-gpio4`, sealed
journal SHA-256
`b76bb27c57af55136042559be4bbc385d6e3498755d3bd39737800703963c514`,
execution-instance SHA-256
`3dc6dff32898768e52f9a6d5d46075b65a33a60c3759d14dbae53009134cc667`,
and exact owned staging path:

`/var/lib/rp1-gpclk-dkms/gate-d/runs/phase5.48-ef96f246b66b/staging/gd-current-supported-kernel-gpio4`

Before mutation, use root-authorized inspection to require that the path is a
real root-owned mode-0700 directory beneath the exact Phase 5.48 staging
parent, contains 866 regular files totaling 4,870,095 bytes, contains no
symlink or non-file/non-directory member, and includes the exact sealed
execution instance. Require the attempt journal to remain root-owned mode 0400,
sealed, complete, recovery-free, output-disabled, and checksum-valid. Require
the module, endpoint, overlay, candidate and predecessor DKMS registrations,
and attempt-2 evidence to be absent and all six controlled services inactive.

Remove that one fully resolved directory recursively, without globbing,
variable-derived broadening, following links, or touching its parent, sealed
attempt evidence, Phase 5.48 input staging, qualification root, pre-root
journal, permanent tools, historical evidence, or unrelated bytes. Then use a
root-authorized probe to require the exact directory absent, the parent staging
directory present and otherwise empty, the sealed evidence and all six
checksums unchanged, and the inactive baseline preserved.

Do not retry or resume attempt 1 and do not begin attempt 2. Do not modify the
frozen Phase 5.48 executor or control bytes. Record as a mandatory successor
release gate that every successful attempt must dispatch
`remove-attempt-residue` before `audit-residue`, and that protected-path
absence checks must run with sufficient authority and distinguish permission
denial from absence.

Output remains disabled. GPIO output, active clock output, DMA submission,
Si5351 or SDR operation, antenna connection, transmission, RF, `/dev/mem`,
forced module removal, general upgrade, and unreviewed persistent boot mutation
remain prohibited.
