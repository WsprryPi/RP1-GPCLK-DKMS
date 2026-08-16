<!-- SPDX-License-Identifier: MIT -->

# Phase 5.36 freeze and representative-build adversarial assessment

Status: accepted for Phase 5.36 control-set construction; target execution is
not ready or authorized by this evidence.

The active candidate is consistently `0.0.0-phase5.36` at freeze commit
`20f7a21ad8601f2e2fd4dec4640ea919acc22ce0`. Phase 5.35 controls,
authorization, staging, failure, and review evidence were not rewritten. Two
isolated release units validated independently and matched byte-for-byte.

The exact checksummed archive compiled unprivileged on wspr5 against the
recorded canonical stock headers. Module, UAPI, administrator, diagnostics,
pre-root, outer-executor, helper, compiler, configuration, and
`Module.symvers` identities are explicit. The changed pre-root hash
`4910e737830495b0fe6b8f41e3947b62968a2bcee32b0178288a37a3b525d7b8`
contains the recovered-ledger handoff; its focused and full offline tests passed
before the freeze.

Initial and final inactive baselines agree. No DKMS administration,
installation, live-ledger mutation, module or overlay action, service/boot
change, GPIO, clock, DMA, Si5351, SDR, transmitter, antenna, reboot,
transmission, or RF effect occurred. This cannot qualify lifecycle, cleanup,
coexistence, timing, routes, or RF behavior.

The next control set must use envelope schema version 3, bind the exact live
terminal Phase 5.34 recovered ledger and a unique bounded archive path, retain
the Phase 5.31 predecessor graph, and independently validate every resulting
hash. No actionable finding remains within this build-only slice.
