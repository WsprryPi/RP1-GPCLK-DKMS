<!-- SPDX-License-Identifier: MIT -->

# Phase 5.40 signing probe and preflight recovery prompt

Repair the Gate D stock-kernel signing-policy preflight exposed by the preserved
Phase 5.39 first-attempt failure. Treat
`/proc/sys/kernel/module_sig_enforce` as optional rather than authoritative by
itself. For the non-enforcing row, require exact kernel configuration evidence,
the kernel command line, any present sysctl, and any present lockdown state to
agree. Accept an absent sysctl only when the exact kernel configuration states
`# CONFIG_MODULE_SIG is not set` and no command-line or lockdown contradiction
exists. Fail closed for missing or ambiguous configuration, unsafe paths,
malformed values, read errors, enforcement, or contradictory sources.

Add deterministic present-zero, present-one, absent-with-signing-disabled,
unsafe/unreadable, missing-config, and contradictory-policy tests. Record the
derived policy and evidence source in preflight evidence without weakening the
separate signature-enforcing rows.

Create and independently validate an exact terminal-recovery plan for the
immutable Phase 5.39 `gd-current-supported-kernel-gpio4` failure. Authenticate
the source evidence directory, journal, evidence manifest, operation,
document/index/executor hashes, completed `create-evidence` step, pending
`capture-preflight` step, inactive baseline, and output-disabled safety state.
Recovery may only create a new immutable terminal attestation referring to the
preserved failure; it must not alter or delete the source evidence, package,
qualification root, ledgers, services, DKMS state, module state, overlays, GPIO,
clock, DMA, Si5351, SDR, transmitter, boot state, or RF state.

Run focused and complete offline validation, perform an adversarial review,
and commit and push the successor implementation and recovery plan. Do not run
the recovery on `wspr5`, create a new freeze or representative build, stage a
new control set, or begin another lifecycle attempt. Those are separate gates.
