<!-- SPDX-License-Identifier: MIT -->

# Phase 5.42 snapshot-bound freeze, representative build, and control-set prompt

Preserve the independently validated canonical wspr5 live-target snapshot with
SHA-256 d228a5fe8eaa52a2fa44d003947d51b2a3a6798e4535c0570c3836ab5b283b9a.
Freeze successor 0.0.0-phase5.42 from reviewed commit
005e5d4095ed3361bdaa14831c841449615e264b. Bind all target-derived facts solely
to that snapshot; do not infer or copy target state from an earlier control set.
Preserve every Phase 5.41 and earlier execution, failure, recovery, and control
artifact unchanged.

Advance only active candidate identities, deterministic fixtures, release
paths, and new Phase 5.42 release notes. Run focused freeze checks and the
complete offline suite, then commit and push the clean freeze. Use the exact
freeze commit timestamp as SOURCE_DATE_EPOCH to create two isolated,
non-publishable release units. Independently validate both and require byte
identity.

Transfer one checksummed unit to a new wspr5 evidence directory. Without
installation or privilege, build the module and Gate D helpers directly from
the archive against the snapshot-bound stock headers. Revalidate exact host,
boot, kernel, headers, configuration, compiler, signing policy, current
administrator ledger, terminal recovery, complete 28-path installed inventory,
inactive services, inactive runtime, and physical safety. Record exact input,
environment, transcript, and output hashes. The representative build proves
build compatibility only.

Generate a distinct deterministic schema-3/schema-4 Phase 5.42 control set.
Every target-derived field must compare against the canonical snapshot through
the independent validator. Require 38 indexed attempts, ten ready rows, five
deferred environmental rows, complete typed Phase 5.39-to-Phase 5.42 package
transitions, retained-tool closure, terminal recovery boundaries, exact release
inputs, and hash closure. Keep targetExecutionApproved and executionReady false.
Regenerate into a clean temporary tree, require byte identity, run focused and
complete offline validation, and perform a separate adversarial review.
Correct and retest every actionable finding.

Do not install, add, remove, or administer DKMS; replace package paths; mutate
ledgers; load, bind, unbind, or unload a module; activate overlays; alter boot
or services; reboot; access GPIO; enable clocks; submit DMA; operate the
separate I2C Si5351 path; operate SDR or transmitter equipment; connect an
antenna; transmit; produce RF; stage target lifecycle inputs; request lifecycle
authorization; or execute a lifecycle attempt.

Exit only with a clean pushed freeze, byte-identical releases, passing exact
representative build, deterministic snapshot-bound control set, independent
clean review, pushed evidence/control commits, and a clean synchronized
worktree.
