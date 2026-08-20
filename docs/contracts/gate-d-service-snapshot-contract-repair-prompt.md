<!-- SPDX-License-Identifier: MIT -->

# Gate D canonical service-snapshot contract repair prompt

Repair the offline Gate D control-generation boundary exposed by Phase 5.47
attempt 1. Do not alter, regenerate, reauthorize, stage, or execute the sealed
Phase 5.47 control set.

Add a deterministic generator primitive that binds every planned service's
`requiredPreState` to the canonical live-target snapshot. An inactive snapshot
service must use `requiredPreState: inactive` and `action: preserve`; an active
snapshot service must use `requiredPreState: active` and
`action: stop-then-restore-exact`. Reject missing, duplicated, unknown, or
unsupported service states.

Add an independently implemented validator that compares every generated
attempt service contract with the canonical snapshot and requires all attempt
documents to use one identical service contract. It must reject the current
Phase 5.47 mismatch, a mutated service state, a mutated action, incomplete
coverage, duplicates, and inconsistent documents.

Exercise the successor behavior without writing new release controls: bind a
copy of the Phase 5.47 target plan to its canonical snapshot, generate all 38
attempts in memory, require the independent validator to pass, and require the
stateful fake executions to finish with exact service restoration and output
disabled. Preserve the current Phase 5.47 files byte-for-byte.

Run focused tests, deterministic Phase 5.47 generation checks, the complete
offline suite, documentation links, and whitespace validation. Perform a
separate adversarial review. No target access, service operation, freeze,
representative build, control-set publication, authorization, staging, DKMS,
module, overlay, GPIO, clock, DMA, Si5351, SDR, antenna, transmission, or RF
activity is permitted.
