<!-- SPDX-License-Identifier: MIT -->

# Phase 5.31 authorized-execution adversarial assessment

Status: blocked safely at transition verification; inactive baseline restored

The target execution confirmed that Phase 5.31 safely accepts an already-absent
predecessor only after exact empty DKMS status checks. It also exposed a missed
cross-document invariant: every pre-root `installedTools` identity must equal
the corresponding bootstrap-plan installed or retained-tool identity and the
frozen source installation semantics. Internal envelope self-consistency alone
is insufficient.

The stale administrator hash was not patched, copied over, or accepted. The
sealed execution stopped before any lifecycle attempt. Recovery preserved the
failure evidence, verified every administrator-owned byte and every partial
root transition byte, restored the inactive target baseline, and retained the
staged inputs for review.

The next gate must correct the Phase 5.31 control set without changing the
frozen candidate, rebuild all dependent hashes including the execution
instance and self-authenticating envelope, add positive and negative
cross-document installed-tool equality tests, independently review the complete
graph, and obtain fresh target authorization. The failed envelope and its
authorization must not be reused.

No module load or binding, overlay activation, GPIO, clock, DMA, Si5351,
transmitter, SDR test, antenna, transmission, reboot, or RF action occurred.

## Corrected-run reassessment

The corrected pre-root transition later committed safely, but the first
permanent-executor dispatch exposed a separate blocker before `execute()`:
Python function-local name binding made `sys` unavailable in the execute
branch. Validation and planning did not cover the real CLI dispatch path, so
their success was insufficient evidence. The target remained output-disabled
and unmodified by the attempt.

The smallest repair removes the redundant branch-local import and adds a
subprocess regression that enters the real execute CLI path and requires its
explicit fail-closed authorization error, with no `UnboundLocalError`. This
repair changes an archive-installed executable, so Phase 5.31 remains frozen
and blocked. A successor must rebuild, re-freeze, repeat representative build
evidence, regenerate and independently validate every hash-bound Gate D
control, and receive fresh authorization before target execution.
