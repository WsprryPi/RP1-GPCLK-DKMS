<!-- SPDX-License-Identifier: MIT -->

# Phase 5.40 signing probe and preflight recovery review

## Result

PASS for the bounded offline Phase 5.40 successor. The signing-policy probe now
fails closed across the reviewed evidence sources without requiring a sysctl
that the target kernel does not expose. The terminal-recovery plan is bound to
the preserved Phase 5.39 failure and cannot continue or restart that attempt.

This result does not authorize or claim target recovery, a new freeze, a
representative build, control-set staging, or lifecycle execution.

## Failure evidence reviewed

The first Phase 5.39 attempt stopped before DKMS, overlay, module, GPIO, clock,
DMA, Si5351, SDR, transmitter, or RF operations. The target's exact
`/boot/config-6.18.34+rpt-rpi-2712` states
`# CONFIG_MODULE_SIG is not set`; its command line does not request module
signature enforcement; lockdown is absent; and
`/proc/sys/kernel/module_sig_enforce` is absent. The previous probe incorrectly
treated that optional sysctl as mandatory.

## Adversarial assessment

- An absent sysctl is accepted only with the exact running-kernel configuration
  explicitly disabling module signing and no command-line or lockdown
  contradiction.
- A signing-enabled configuration with no runtime enforcement evidence rejects
  rather than being inferred non-enforcing.
- Missing or ambiguous configuration, malformed or unsafe evidence paths,
  enforcing values, and contradictory sources reject the preflight.
- Deterministic tests cover absent-with-disabled, present-zero, present-one,
  unsafe, missing-config, and contradictory-policy cases.
- Phase 5.39 validation reads its frozen executor payload from the sealed source
  commit when the current successor file differs; it does not silently bless
  mutable bytes as predecessor evidence.
- The recovery document authenticates the exact source directory, journal,
  manifest, failed operation, completed and pending boundary, document, index,
  executor, inactive baseline, and output-disabled safety state.
- Recovery can create only a new immutable terminal attestation. It cannot
  alter the source evidence or begin another attempt.

No actionable finding remains within this offline scope.

## Validation

- `python3 tests/check_gate_d_outer.py`
- `python3 tests/check_gate_d_residue.py`
- `python3 tests/check_gate_d_phase5_39_control_set.py`
- `make check`
- `git diff --check`

All checks passed. Linux-only client compile checks remained expected skips on
the macOS development host.

## Next gate

Separately authorize the exact terminal recovery on `wspr5`. After recovery is
complete and independently checked, construct and validate a new frozen
successor, representative target build, and complete control set before any
new lifecycle execution authorization.
