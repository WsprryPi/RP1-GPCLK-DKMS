<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.26 target-execution authorization

On 2026-08-16 the operator explicitly authorized execution of the exact
Phase 5.26 output-disabled Gate D control set recorded by commit
`8dda6c6f9aac44c28ddef2351beb4378c8e2e8f2` on `wspr5`.

The authorization covers only the ten `ready` rows and their 38 reviewed
attempt documents: exact test-owned DKMS lifecycle, output-disabled module and
allowlisted overlay administration, bounded attempt-owned failure injection,
named-service quiescence and exact restoration, reversible selection of the
two reviewed installed stock kernels, planned reboot after recovery preflight,
sealed evidence, recovery, and complete attempt-owned cleanup.

The five `deferred-environmental` rows remain outside executable coverage.
Live output, active pinctrl, clock enablement, DMA submission, GPIO output,
Si5351 operation, transmitter keying, SDR operation, antenna connection, RF,
`/dev/mem`, a custom kernel, forced removal, a general upgrade, unrelated
cleanup, and unreviewed persistent boot changes remain prohibited.

Authorization is fail-closed on exact identity, conflict, physical-safety,
rescue-readiness, staging, schema, hash, and final-state preflight. Any
unresolved mismatch stops before the affected mutation and does not authorize
an improvised substitute.
