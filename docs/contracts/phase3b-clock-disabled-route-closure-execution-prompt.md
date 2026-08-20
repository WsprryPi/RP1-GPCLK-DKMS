<!-- SPDX-License-Identifier: MIT -->

# Phase 3B clock-disabled dual-route target-closure execution prompt

## Mission and exit condition

Act as the target kernel-module maintainer, qualification-evidence custodian,
and adversarial reviewer for `WsprryPi/RP1-GPCLK-DKMS`.

Close the remaining Phase 3 target gate on one exactly named and authorized
Raspberry Pi 5 / RP1 target. Validate GPIO4 and GPIO20 independently with live
output disabled; prove route identity and mismatch rejection, shared-endpoint
conflict rejection, safe-state preservation, process and descriptor lifetime,
partial-acquisition cleanup, and repeated administrative route changes. Return
the target to a verified baseline and preserve a complete, portable,
checksummed evidence bundle.

Phase 3B is complete only when every mandatory assertion below passes for both
routes on the exact recorded identity, the evidence survives independent
relocation and verification, a separate adversarial assessment has no
unresolved objective finding, and the final target state is proved clean.

Only after Phase 3B closes may work advance to Phase 4 timing and controlled
live-output qualification.

## Required authorization record

Before any target mutation, record the user's exact authorization in the
execution evidence:

- target hostname and expected Raspberry Pi model/revision;
- permitted connection method and administrative account;
- exact source commit or immutable source-tree digest;
- permission to build, install, sign, load, bind, unbind, and unload this test
  module on that target;
- permission to apply and remove only the named Phase 3B overlays;
- permission to create and remove test files, a disposable signing key, and an
  evidence directory;
- explicit confirmation that output must remain disabled; and
- explicit exclusions: no boot/config changes, reboot, service changes, active
  pinctrl selection, clock preparation/enabling/rate changes, DMA descriptor
  submission, GPIO output, transmitter keying, transmission, SDR capture, or
  RF output.

If the exact target or any required administrative operation is not expressly
authorized, stop before mutation and report Phase 3B blocked. Authorization for
offline repository work or a previous GPIO4 phase does not authorize Phase 3B.

## Governing contracts and immutable inputs

Follow, in order:

1. `AGENTS.md`;
2. `docs/contracts/rp1-gpclk-dkms-module-contract.md`;
3. `docs/contracts/phased-plan.md`;
4. `docs/contracts/phase3-gpio20-interface-freeze-execution-prompt.md`;
5. `docs/development/decisions/0005-phase2e-gpio4-clock-disabled.md`;
6. `docs/development/decisions/0006-phase3-interface-freeze.md`;
7. canonical UAPI `include/uapi/linux/rp1_gpclk.h` and
   `uapi-identity.json`; and
8. the compatibility-manifest v1 schema and route-specific evidence rule.

Phase 3B consumes the frozen ABI, overlay names, route values, DT properties,
compatible, module/device names, and manifest vocabulary. Do not change a
frozen interface merely to make a target test pass. An interface defect stops
the phase for reviewed correction and a full restart from the immutable source
identity.

## Safety invariants

Continuously enforce all of the following:

- GPIO4 and GPIO20 remain inputs and never select `gpclk0`.
- GPCLK0 prepare and enable counts remain exactly zero.
- The driver never calls clock prepare/enable, changes rate/parent, selects the
  active pinctrl state, prepares/submits DMA, or performs raw MMIO.
- Rate-protection count is zero when absent and exactly the expected
  module-owned count only while one production endpoint is bound.
- At most one route endpoint owns GPCLK0/DMA/module resources.
- Applying or acquiring one route does not claim, remux, drive, bias, or alter
  the other route.
- Route changes occur only through remove-to-absent then apply. In-place or hot
  route mutation is unsupported and must not be attempted.
- Every command has a TERM deadline, a KILL deadline, recorded timestamps and
  status, and deterministic expected-success or expected-failure semantics.
- Cleanup is armed before the first mutation and remains armed until explicit
  final absence and evidence verification pass.
- Any unexpected pin state, nonzero prepare/enable count, cleanup fault,
  timeout, kernel warning, or ambiguous identity stops the run and invokes
  bounded cleanup.

No clean result proves exclusion against direct-MMIO or hostile/uncoordinated
kernel software.

## Required Phase 3B assets

Before target execution, inspect and, where necessary, implement deterministic
assets for this phase:

- a Phase 3B target runner derived from the reviewed Phase 2E evidence model,
  parameterized only where that preserves exact route-specific assertions;
- machine validation of runtime DT route, pin, clock, DMA provider/request,
  common RP1 parent, provider resource, divider target, module identity, UAPI
  identity, and queried route;
- a UAPI client that can query, acquire with an expected route, require a route
  mismatch failure, hold an acquired descriptor, prove ownership exclusion,
  release, and report exact statuses;
- production GPIO4 and GPIO20 overlays;
- invalid-route and GPIO20/GPIO4 route-pin-mismatch fixtures;
- route-specific pin-conflict, missing-state, and unavailable/bad-DMA fixtures
  where needed to prove each unwind path without selecting an output;
- strict dmesg-delta extraction based on intact baseline-prefix proof;
- a diagnostic classifier that accepts only exact, reviewed, expected fixture
  messages and rejects warning-or-higher faults and near matches;
- immutable command ledger, raw identity captures, source/artifact hashes, and
  relocatable evidence manifest; and
- offline static checks proving the runner cannot select the active state or
  invoke clock/DMA/output operations.

Inspect every test implementation before running it. A fixture that cannot
prove the assertion its name suggests must be renamed or corrected; do not
overclaim from an earlier failure point.

## Pre-mutation gate

Complete all items before installing, loading, or applying an overlay:

1. Verify the repository branch, commit, worktree, upstream state, and absence
   of unrelated changes. Preserve any user work; stop on overlap.
2. Run the complete offline suite twice, warnings fatal where supported,
   including SPDX, UAPI hash/semantics, manifest route isolation, overlay
   symmetry/safe states, lifecycle/resource tests, target-runner static checks,
   ShellCheck, documentation links, and whitespace.
3. Verify the exact target hostname, model/revision, running kernel, matching
   header packages, compiler, architecture, base FDT, firmware/bootloader,
   module-signing policy, debugfs clock visibility, and required utilities.
4. Verify no prior test module, device node, overlay, holder/client process,
   installed module copy, or conflicting GPIO4/GPIO20 consumer exists.
5. Capture full normal and warning-or-higher dmesg baselines.
6. Capture GPIO4 and GPIO20 pinctrl states and GPCLK0 rate, parent, prepare,
   enable, and protect counts. Require both pins input/none, no GPCLK function,
   and all owned counts zero.
7. Create a new, previously nonexistent evidence directory and disposable work
   directory. Refuse reuse or append mode.
8. Record the authorization, start time, boot ID, source identity, target
   identity, tool versions, and every unavailable observation.

Failure of any pre-mutation assertion leaves the target untouched and Phase 3B
open.

## Build and artifact-identity matrix

1. Build the module with warnings fatal against the exact running stock kernel
   headers. Record compiler, configuration, architecture, module version,
   canonical UAPI version/hash, vermagic, build ID, and result.
2. Compile every production and negative overlay against the exact matching
   Raspberry Pi DT binding package. Decompile each DTBO and machine-check its
   compatible, route, pin, clock ID, DMA request, state names, pin function,
   safe/default input properties, and other-pin absence.
3. Sign a disposable tested copy when supported. Record signing configuration,
   signer metadata, selected installed module path, and byte equality between
   built/tested/installed artifacts. Classify signature enforcement truthfully;
   malformed ELF rejection is not signature rejection.
4. Validate the installed module before loading and prove that `modprobe`
   resolves to the exact installed bytes.
5. Load with no bound node. Require no device endpoint, unchanged pins, zero
   prepare/enable/protect counts, and no new unclassified diagnostics.

Build, signing, load, or bind success is compatibility evidence only and never
qualifies live GPIO or RF behavior.

## Route-independent baseline helper

Implement one assertion used before and after every matrix row. It records and
requires:

- selected-route pin input/none and not GPCLK;
- other-route pin input/none and not GPCLK;
- GPCLK0 prepare and enable zero;
- protect count equal to the row's explicit expected value;
- expected bound-device and `/dev/rp1-gpclk` presence/absence;
- exact overlay set;
- no unexpected module/client/holder process or installed artifact; and
- no cleanup-fault latch.

Do not reduce this to a final-only check.

## GPIO4 independent clock-disabled matrix

Using only `rp1-gpclk-gpio4`:

1. Apply the overlay and require exactly one bound device, restrictive
   `0600 root:root` endpoint, runtime DT route 1/pin 4, correct providers and
   resource identity, GPIO4 input, GPIO20 input/unclaimed, prepare/enable zero,
   and expected protect count.
2. Query and require route GPIO4, ABI/module/build/compatibility identities,
   implemented clock-disabled capabilities, and no live-eligible capability.
3. Acquire with expected GPIO4 and release successfully. Prove lease ownership,
   single-owner exclusion, unchanged pins/clocks, and complete release.
4. Acquire with expected GPIO20 and require `EINVAL` before lease or ownership
   mutation. A subsequent correct GPIO4 acquisition must still succeed.
5. Apply the GPIO20 production overlay while GPIO4 is bound. Require explicit
   shared-endpoint `EBUSY`, no second device, unchanged first endpoint, both
   pins safe, and exact expected diagnostics.
6. Exercise GPIO4 pin conflict, missing active state, bad/missing DMA, and
   duplicate endpoint fixtures. Require failure at the intended gate, release
   of only module-owned resources, no device leak, and unchanged safe state.
7. Hold an open descriptor across unbind. New opens must fail; the old
   descriptor remains safely closeable; resources release; unload remains
   blocked while referenced; close then permits unload/reload/rebind.
8. Kill an acquired holder with `SIGKILL`, require the exact wait status,
   ownership/reference release, successful reacquisition, unbind, and unload.
9. Remove the overlay and require the complete absent baseline.

GPIO4 Phase 2E evidence is regression context only. This matrix must pass
against the exact Phase 3B source and target identity.

## GPIO20 independent clock-disabled matrix

Repeat the complete applicable GPIO4 matrix using only
`rp1-gpclk-gpio20`, with no inherited result:

1. Require runtime route 2/pin 20 and independently resolve the GPIO20 pinctrl
   group/function representation.
2. Require GPIO20 input, GPIO4 input/unclaimed, prepare/enable zero, correct
   protect count, exact GPCLK0/DMA identity, and restrictive endpoint.
3. Query route GPIO20; correctly acquire/release expected GPIO20; reject
   expected GPIO4 with `EINVAL` before ownership mutation.
4. While GPIO20 is bound, apply GPIO4 and require the same explicit shared-
   endpoint conflict without disturbing GPIO20 or either pin.
5. Exercise invalid route 0/3/arbitrary and GPIO20-pin/GPIO4-route mismatch.
   Require DT validation failure before endpoint/resource ownership.
6. Exercise GPIO20-specific pin conflict, missing state, bad/unavailable DMA,
   duplicate endpoint, open-descriptor unbind/unload, process death, recovery,
   and cleanup. If a GPIO4 fixture is claimed to apply generically, prove from
   its DT and observed failure point that it actually tests GPIO20; otherwise
   create a GPIO20 fixture.
7. Remove the overlay and require the complete absent baseline.

No GPIO4 result may fill a GPIO20 evidence field or compatibility assertion.

## Repeated administrative route-change matrix

Starting from loaded module/no overlay/complete absence of an endpoint, execute
at least three full cycles of each sequence:

```text
GPIO4 apply -> query/acquire/release -> GPIO4 remove -> prove absent
GPIO20 apply -> query/acquire/release -> GPIO20 remove -> prove absent
```

and:

```text
GPIO20 apply -> query/acquire/release -> GPIO20 remove -> prove absent
GPIO4 apply -> query/acquire/release -> GPIO4 remove -> prove absent
```

For every transition:

- record bounded command/status/timestamps;
- verify the bound route and reject the other route;
- prove both pins safe, prepare/enable zero, and expected protect count;
- prove no old endpoint, lease, descriptor, device, DT node, overlay,
  compatibility identity, or failure latch survives removal;
- prove the next route receives a fresh valid endpoint and lease;
- preserve complete dmesg attribution; and
- stop on the first deviation rather than continuing a contaminated cycle.

Also attempt removal while a route is acquired/open under the reviewed
lifetime procedure. Prove the old descriptor closes safely, new opens fail,
resources become absent, and the next administrative route binds cleanly.

Do not attempt direct property mutation, overlay replacement without an absent
state, or any operation that selects the active pinctrl state.

## Negative and recovery matrix

1. Invalid route value, arbitrary GPIO, and mismatched route/pin fail before
   resource ownership.
2. The second production route fails while the first owns the shared endpoint.
3. Pin conflict, clock-rate-protection conflict, unavailable DMA, missing state,
   map failure where safely injectable, misc registration failure where
   deterministically injectable, and every implemented partial-probe failure
   release resources in reverse order.
4. Process death, descriptor close, unbind with open descriptor, rejected
   unload, successful post-close unload, reload, and rebind retain Phase 2
   lifetime guarantees for both routes.
5. Simulate the reviewed missing/incompatible kernel-header update failure
   without changing the running kernel or boot configuration. Require nonzero
   result, no candidate activation/installation, then prove the known-good
   exact artifact still completes one GPIO4 and one GPIO20 safe bind cycle.
6. Any cleanup/readback/identity ambiguity must latch or classify fail-closed as
   required by the current implementation; it cannot be downgraded to a pass.

## Kernel diagnostics and evidence integrity

- Retain full dmesg baselines and finals. Require each baseline to be an exact
  intact prefix before extracting the suffix.
- Classify all warning-or-higher suffix messages. Accept only exact expected
  fixture-specific diagnostics with exact count and errno. Reject generic or
  near-match allowlists, `WARNING`, `BUG`, `Oops`, call traces, memory/lifetime
  faults, DMA faults, cleanup errors, and unexplained platform-probe failures.
- Record every command, expected result, actual status, timeout, pre/post
  invariant, and cleanup result in an immutable ledger.
- Hash the source tree, canonical UAPI, module before/after signing, installed
  module, every DTS/DTBO, runtime DT dump, evidence file, and command ledger.
- Generate the final manifest only after writers close and disposable target
  assets are removed. Use relative paths and verify after extracting the bundle
  to a different directory.
- Preserve failed and superseded attempts separately and label why they are not
  acceptance evidence. Never delete or rewrite inconvenient evidence.

## Final cleanup and absence proof

Before declaring success:

1. Close/terminate/reap every client and holder with recorded status.
2. Remove every overlay applied by the phase in reverse order and verify each
   removal.
3. Unbind/unload the module, remove only the installed test artifact and
   disposable signing material created by the phase, and refresh dependencies
   if required.
4. Prove no test overlay, module, device node, bound device, client, holder,
   installed copy, work directory, or unexpected process remains.
5. Prove GPIO4 and GPIO20 input/none and not GPCLK; GPCLK0 prepare, enable, and
   protect counts zero; and no cleanup-fault latch.
6. Prove no boot, service, network, transmitter, SDR, GPIO-output,
   transmission, or RF configuration changed.
7. Capture final dmesg and complete exact-prefix/delta classification.
8. Close the evidence ledger, create and verify the relative SHA-256 manifest,
   archive the bundle, independently extract/verify it, and record the outer
   archive hash.

Cleanup failure makes Phase 3B fail even if every earlier row passed.

## Compatibility and qualification ceiling

A Phase 3B pass proves only clock-disabled administrative behavior for the
exact recorded target, kernel, firmware, DT, overlays, module, UAPI, and source
identity.

- It does not qualify clock activation, divider sequencing, timing, jitter,
  live GPIO, transmission, RF, any WsprryPi mode, another kernel, another Pi,
  another drive, or another route identity.
- GPIO20 receives no GPIO4 qualification.
- Build success remains no higher than `Compatible-unqualified`.
- Any later `Experimental` classification requires the separately defined
  administrator enrollment and product policy.
- `Qualified` remains impossible until Phase 4 supplies complete independent
  timing, cleanup, recovery, and RF evidence for each route and mode.

## Independent adversarial assessment and reinjection loop

After a complete maintainer run, perform a separate review that attempts to
falsify:

- authorization scope and exact target/source/artifact identity;
- the clock-disabled and no-RF boundary;
- GPIO20 pinmux/DT/runtime identity independent of GPIO4;
- route/pin mismatch rejection before ownership;
- other-route safety and non-ownership;
- simultaneous endpoint and resource-conflict rejection;
- prepare/enable/protect accounting;
- descriptor, process, unbind, unload, callback, and object lifetime;
- partial-probe reverse cleanup and ordered endpoint release;
- three-cycle route changes in both directions with true absent transitions;
- dmesg attribution and exact diagnostic classification;
- evidence completeness, immutability, portability, and source mapping;
- final target absence and restoration;
- compatibility ceiling and absence of inherited qualification; and
- repository cleanliness and documentation accuracy.

Append every objective finding to the reinjectable findings log below. Correct
the prompt, runner, implementation, fixtures, tests, evidence, or prose as
appropriate. Rerun every affected test plus the complete offline and target
safety matrices from a clean baseline, then repeat independent review. Continue
until no objective finding remains. A blocked, unavailable, ambiguous, or
unobserved mandatory assertion keeps Phase 3B open; it is never relabeled as a
pass or waived implicitly.

## Required completion report

Lead with `Phase 3B PASS` or `Phase 3B OPEN` and include:

- exact source commit/tree identity and target identity;
- both route results and every matrix row disposition;
- evidence bundle path, inner-manifest result, and outer SHA-256;
- exact offline and target checks with results and skips;
- final GPIO4/GPIO20 and GPCLK0 state;
- all hardware/system operations actually performed;
- explicit confirmation that no active clock, DMA execution, GPIO output,
  transmission, SDR, or RF work occurred;
- licensing, UAPI, overlay, manifest, and documentation impact;
- adversarial findings, reinjections, reruns, and final disposition;
- remaining validation and the exact Phase 4 gate; and
- Git branch/status plus whether anything was staged, committed, pushed, or
  published.

Do not begin Phase 4 in the same authorization or execution. Stop after the
Phase 3B report and wait for separately bounded GPIO and RF authorization.

## Reinjectable findings log

1. Pre-mutation review found that `QUERY.compatibility_id` was still hard-coded
   to `phase2e-gpio4-clock-disabled`, which would falsely attach a GPIO4-only
   identity to GPIO20. The Phase 3B implementation must use a route-neutral
   compatibility identity, bump the prerelease module/DKMS version together,
   and make the target UAPI and DT validators require an explicit expected
   route and route/pin pair before any target mutation.
2. The first correction generalized the Phase 2E UAPI client and DT checker in
   place, which would make the historical Phase 2E runner non-reproducible.
   Restore the Phase 2E assets byte-for-byte and add separately named Phase 3B
   route-parameterized client and DT validators.
3. Asset review found that GPIO4-only negative overlays could not prove GPIO20
   pin conflict and partial-probe cleanup. Add GPIO20-specific conflict,
   duplicate-endpoint, missing-active, and bad-DMA fixtures, plus a Phase 3B
   diagnostic classifier and static target-runner gate.
4. The first complete offline run rejected four target-runner shell constructs:
   an errexit-ambiguous negated pipeline, a dependent same-line `local`,
   unbounded word splitting for route order, and an undocumented child-shell
   expansion. Replace them with explicit control flow, separate locals, a
   parsed array, and a narrowly justified ShellCheck suppression.
5. Restoring the historical Phase 2E validators initially left one extra blank
   line at each EOF, violating byte preservation and the whitespace gate.
   Remove those lines and require a clean `git diff --check` before transfer.
6. Target attempt 1 stopped in the offline preflight because the macOS source
   archive retained Apple provenance/xattr records that extracted as non-UTF-8
   metadata artifacts. Preserve the failed evidence, require a metadata-free
   archive (`COPYFILE_DISABLE=1`, no xattrs/AppleDouble files), machine-check
   the extracted tree for `._*` files, and repeat from a new target source and
   evidence directory before any module or overlay mutation.
7. Target attempt 2 reached the GPIO4-bound/GPIO20-apply conflict and the
   kernel correctly rejected the second production overlay, but the runner
   treated `dtoverlay` status 1 as an unexpected failure. Preserve the attempt,
   add a bounded expected-overlay-failure helper that never records an
   unapplied overlay for cleanup, prove the first route and both safe states
   remain intact, and repeat the complete matrix from a new baseline.
8. Target attempt 3 passed every functional, repeated-route, recovery, and
   cleanup row but the final classifier expected overlay filenames in runtime
   DT node names. Evidence showed the exact shared node identities and a
   22-line warning set. Narrow the classifier to those observed node names,
   exact errnos, exact per-pattern counts, both pin-conflict lines, and exactly
   22 total lines; preserve attempt 3 and repeat the complete matrix.
9. The first independently verified complete pass exercised the open-descriptor
   unbind lifetime only on GPIO20 and did not explicitly prove that a new open
   fails after unbind or that unload remains blocked after unbind while the old
   descriptor is referenced. Treat this as a lifecycle coverage failure. Run
   the complete sequence independently for GPIO4 and GPIO20, including unload
   rejection before and after unbind, new-open rejection, close, rebind, and
   safe removal.
10. Strengthen the terminal absence assertion to cover the installed module
    artifact and bound-device set, make source-tree hashes relocatable, and
    record the transferred source-archive digest when available. Repeat the
    full target matrix; a lifecycle-only rerun is insufficient.
11. The final staged-diff gate found an extra EOF blank line in four GPIO20
    fixtures and two Phase 3B validators. Removing those lines changes tested
    bytes, even though semantics are unchanged. Treat exact source-to-evidence
    reproducibility as blocking, preserve attempt 5, remove the whitespace,
    and repeat the complete matrix from a fresh metadata-free source snapshot.
