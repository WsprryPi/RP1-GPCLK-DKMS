<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.17 control-set construction adversarial assessment

Status: blocked before target-plan construction

## Intended slice

The slice attempted to bind the exact Phase 5.17 qualification bootstrap into
the route decision, target operation plan, 38-attempt bundle, and execution
instance. It was offline-only and authorized no target contact or mutation.

## Blocking finding

The frozen Phase 5.17 candidate implements the qualification-install CLI, but
its frozen Gate D contracts cannot represent or authenticate that bootstrap:

- target-plan schema version 2 requires an exact top-level key set and rejects
  a `qualificationBootstrap` object;
- its exact tooling set excludes `rp1-gpclk-admin.py`, so the command that
  performs the bootstrap has no bound source or installed identity;
- the execution-instance schema requires an exact execution-policy key set and
  rejects a bootstrap-plan path and digest; and
- the attempt generator begins after permanent tools are assumed installed, so
  none of the 38 documents owns, records, or recovers the prerequisite
  bootstrap transaction.

Synthetic adversarial mutations confirmed that adding a bootstrap object,
adding the administrator to tooling, or adding a bootstrap reference to the
execution instance all fail closed. A separate unreferenced document would be
security theater: it could be swapped without invalidating the target plan,
attempt index, or execution instance.

## Decision

Phase 5.17 must not be patched in place and no apparently complete control set
may be generated from it. Its representative-build result remains valid only
as build compatibility evidence; it supplies no Gate D readiness.

A distinct successor must add, before candidate freeze:

1. a closed qualification-bootstrap plan schema binding the exact candidate,
   qualification identity, administrator source and installed hashes, literal
   argv, transaction journal, expected baseline, and cleanup/recovery rules;
2. target-plan support that hashes and validates that subordinate plan;
3. execution-instance policy fields binding the subordinate plan and identity;
4. outer-executor preflight and dispatch for bootstrap, including interrupted
   bootstrap recovery and verified transition to an empty inactive DKMS/module
   baseline while retaining exact permanent tools; and
5. stateful offline tests for missing, swapped, stale, symlinked, partially
   installed, interrupted, and cleanup-failure states.

Only after that successor passes adversarial review may it be frozen, built on
wspr5 under separate authorization, and used to construct a renewed 38-attempt
control set.

## Activity boundary

No Raspberry Pi was contacted. No package, DKMS, module, overlay, service,
boot, reboot, GPIO, pinctrl, clock, DMA, Si5351, SDR, transmission, or RF
activity occurred.
