<!-- SPDX-License-Identifier: MIT -->

# Phase 5.46 authenticated target staging and pre-root prompt

Execute only the staging and authenticated pre-root transition authorized at
commit `6b3dcc83c817e6c0011e6dde649b146df88abc91`. Bind this slice to frozen
source `b43e2744b212f5bc53ad40584254f52310af4684`, archive SHA-256
`0e0debdd96560602bd61457afc59782cfad2a4fb1b6f9b54e0d2505453e6c8f2`,
authorized execution-instance SHA-256
`cece70ab06d8a3b6de0240851b1ec2d7612e2d699f0f6c97de57a42da0687f2e`,
schema-5 pre-root envelope SHA-256
`f71efda6d310137d4372c98a8c90d2104ff57fe744159dd84c6a7b06844d3dd5`,
unchanged attempt-index SHA-256
`e1858c68af8362a3c9ac969b5335317617e8e67491ddc916c3190c2eb6a8243d`,
and canonical snapshot SHA-256
`bc4c307350d6e74c9cbb85ef890fbaf0e8ad969ecdeb661a98703b70bd4a1859`.

Immediately before staging, run the committed read-only capture and independent
validator with the same terminal recovery journal and physical declarations.
Require byte identity with the 7,057-byte canonical snapshot, inactive runtime,
six inactive services, terminal-complete Phase 5.45 ledger, exact 28-path
predecessor inventory, authenticated recovery, an unused SDR, no antenna, and
the disconnected and unused separate I2C Si5351 path. Remove transient capture
files. Stop before staging on any difference.

Only after an exact match, require the declared Phase 5.46 input directory to
be absent, create that one directory, and populate every envelope input from
the checksummed release unit, committed authorized controls, frozen matrix
policy and eight-module graph, plus the separately sealed envelope. Extract
only the authenticated archive into its declared path. Verify the exact path
set and every SHA-256 on the target. Run the exact archived outer executor in
read-only pre-root validation mode and require success.

Invoke the authenticated schema-5 pre-root transition exactly once. It may
archive only the exact snapshot-bound Phase 5.45 administrator ledger, install
the exact Phase 5.46 qualification package, remove only declared runtime
residue, and create the authenticated qualification root. On failure, stop;
invoke only journal-authorized `--resume` recovery, and return without starting
an attempt.

After success, validate the immutable pre-root journal, installed permanent
executor, qualification-root marker, authorized execution instance, matrix
policy, eight-module graph, and attempt index. Stop before lifecycle attempt 1.
Do not execute, resume, skip, or substitute any indexed attempt in this slice.

Output remains disabled. Active pinctrl, clock enablement, DMA submission,
GPIO output, Si5351 operation, transmitter keying, SDR operation, antenna
connection, RF, `/dev/mem`, custom-kernel qualification, forced removal,
general upgrade, and unreviewed persistent boot mutation remain prohibited.

Preserve complete evidence, independently review the result, and commit and
push documentation only. Any identity, state, service, recovery, residue,
cleanup, transition, or safety discrepancy is a terminal stop for this slice.
