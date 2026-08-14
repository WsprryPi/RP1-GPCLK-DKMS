<!-- SPDX-License-Identifier: MIT -->

# Phase 2E authorized clock-disabled target execution prompt

## Outcome and exact authority

Act as the target kernel-module maintainer and adversarial qualification
reviewer for `WsprryPi/RP1-GPCLK-DKMS`. On the exact authorized Raspberry Pi 5
GPIO4 target, install, load, bind, exercise, unbind, unload, and remove the
Phase 2 clock-disabled module. Prove resource-conflict rejection, process-death
cleanup, open-descriptor lifetime, unbind/unload ordering, exact signing-policy
behavior, partial-probe cleanup, and a simulated failed kernel-update build.

This prompt is the separate authorization for those clock-disabled
administrative operations on `wspr5` only. It does not authorize clock
prepare/enable, clock-rate changes, selection of the GPCLK pinctrl state, DMA
descriptor submission, GPIO output, transmission, RF output, boot changes,
reboot, service changes, or tests on another target. GPIO4 must remain an input
with GPCLK0 prepare and enable counts zero before, during, and after every test.
Stop immediately if any invariant cannot be observed or is violated.

## Governing contracts and result ceiling

Follow `AGENTS.md`, the module engineering contract, phased plan, canonical
UAPI, accepted Phase 2A through 2D decisions, and licensing policy. Preserve
the stock `clk-rp1` provider and the Phase 2C inertness boundary: no source in
this phase may call clock prepare/enable or rate-change APIs, select the active
pin state, prepare/submit DMA, use raw MMIO, or depend on private symbols.

A Phase 2E pass closes only the GPIO4 clock-disabled prototype gate for the
exact recorded target identity. It does not qualify GPIO20, another kernel or
Pi, live GPIO, timing, transmission, RF, operator enablement, coexistence with
direct-MMIO software, or a complete release/installer workflow. The exact
identity remains no higher than `Experimental` and only after explicit product
enrollment; it is never `Qualified` without later timing and RF evidence.

## Required repository work

- Add a GPIO4-only overlay whose `default` and `safe` states both keep GPIO4 as
  input with bias disabled and whose unselected `active` state describes only
  the allowlisted GPIO4 GPCLK0 route. The bound node must name exactly GPCLK0,
  the RP1 DMA tick request, and the production compatible string.
- Add negative overlays for a duplicate resource claimant and deliberate
  partial-probe failures. Negative fixtures must remain clock-disabled and
  must not select an output function.
- Add a reviewed target runner with an immutable mutation ledger, bounded
  waits, cleanup traps, exact target allowlisting, and invariant checks around
  every administrative step. Ordinary offline checks must inspect the runner
  and overlays without executing target or system operations.
- Record exact source, UAPI, module, overlay, target, kernel, DT, firmware,
  compiler, build, signature-policy, resource, command, result, diagnostic,
  and final-cleanup evidence. Preserve raw evidence in a checksummed bundle.

## Authorized target matrix

1. Establish baseline identity and safety: exact Pi model/revision, kernel and
   header package, boot/firmware and base-DT identities, GPIO4 input state,
   GPCLK0 rate/parent/protect/prepare/enable counts, no prior overlay/module,
   and no conflicting GPIO4 consumer.
2. Build with warnings fatal against the running stock kernel headers. Compile
   every overlay and machine-check the module metadata and DT contents.
3. Test installation and signing policy. Exercise the exact local signing
   workflow when kernel tools support it; record signature metadata and loader
   behavior. If the exact kernel has signature enforcement disabled or absent,
   label cryptographic rejection `Not applicable on this identity`; do not
   claim it passed. A malformed or mismatched module must still fail closed.
4. Load the module with no bound node, then apply the GPIO4 overlay and prove
   successful bind, restrictive device-node mode, exact DT/resource identity,
   zero clock prepare/enable counts, and GPIO4 input state.
5. Prove exclusive conflicts: a second instance requesting the same GPCLK0
   rate lease/DMA resource must not bind; a process holding the device must
   preserve single-owner semantics; and failure must not disturb the original
   instance or safe state.
6. Hold an open descriptor across unbind. New opens must fail, the existing
   descriptor must remain safely closeable, resources must be released, and
   rebinding must succeed. With a descriptor open, module unload must be
   rejected; after close and unbind, unload must succeed.
7. Kill a process holding the descriptor with `SIGKILL`; prove the descriptor
   and module reference are released, then repeat bind/unbind and unload.
8. Exercise every available partial-probe failure fixture, including missing
   pinctrl state and unavailable/conflicting DMA. Each must fail to bind,
   release only its own acquired resources, leave no device node, keep GPIO4
   input, and keep GPCLK0 prepare/enable counts zero.
9. Simulate a kernel-update build/install failure without changing the running
   kernel or boot configuration. Use an explicit nonexistent or incompatible
   kernel-build identity, require a nonzero result, verify that no candidate
   module becomes active or selected, and then prove the known-good running
   identity still binds safely. Do not reboot.
10. Remove every overlay, module, installed test source, temporary signing key,
    and test artifact created on the target. Prove the final state matches the
    safety baseline: GPIO4 input, GPCLK0 prepare/enable zero, no module/device/
    overlay/test process, no unclassified warning-or-higher kernel diagnostics,
    and no
    boot, service, GPIO-output, transmission, or RF change.

## Evidence requirements

Every matrix row records the command, start/end timestamps, exit status,
expected failure or success, relevant diagnostics, maximum wait, pre/post
invariants, and cleanup result. Capture `dmesg` by cursor/time boundary so old
host messages are not misattributed. Hash the raw evidence bundle and every
module/overlay tested. Record all unavailable observations explicitly.

No clean run proves absence of uncoordinated direct-MMIO or hostile kernel
software. No build, signature, load, or bind result by itself proves lifecycle
safety. No historical WsprryPi custom-provider evidence substitutes for this
stock-module execution.

## Independent adversarial exit loop

After the maintainer run, use a separate reviewer to attempt to falsify:
authorization boundaries; exact target/source/artifact identity; GPIO4-only
route isolation; the absence of clock/DMA/pinctrl activation; provider/clock/
resource/DMA translation identity; conflict rejection; process-death and open
descriptor behavior; unbind/unload safety; partial-acquisition cleanup;
signing-policy claims; simulated update failure and recovery; bounded cleanup;
kernel-log attribution; evidence integrity; compatibility ceiling; and final
target/Git state.

Append every objective finding to the reinjectable findings log below, correct
the prompt, implementation, runner, or evidence, rerun every affected test and
the complete safety suite, and repeat independent review until no objective
finding remains. A blocked or unavailable mandatory assertion keeps Phase 2
open; it must never be relabeled as a pass.

## Exit statement

Phase 2 closes only if every applicable GPIO4 clock-disabled assertion passes
on the exact recorded target, every non-applicable signing-policy assertion is
truthfully bounded, raw evidence is complete and checksummed, the independent
review has no unresolved objective finding, and the target returns to the
proved safe baseline. Otherwise report Phase 2 open with the exact blocker.

## Reinjectable findings log

1. The first target compile rejected an `__aligned_u64` function parameter;
   alignment attributes are valid on the UAPI members but not that parameter.
   The helper now accepts `const __u64 *`, and the exact target build must pass
   with warnings fatal before any module mutation.
2. The initial target snapshot included macOS AppleDouble sidecars, causing the
   SPDX scan to stop before build or mutation. Transfers now suppress metadata
   sidecars, and the target preflight must pass before continuing.
3. Independent review found that the module-inspection runner passed the
   expected kernel release positionally instead of through the required
   `--kernel-release` option. The runner now uses the exact supported CLI and
   must machine-validate the module before installation.
4. The first independent pass found that signing classification was hard-coded
   and conflated malformed ELF rejection with signature rejection. The runner
   now proves `CONFIG_MODULE_SIG` is unset for this identity, records signature
   metadata, labels cryptographic rejection not applicable, and treats the
   malformed module only as an artifact-preflight negative.
5. Cleanup originally ignored removal failures and did not terminate the
   descriptor-holder child. Cleanup now tracks overlays before application,
   bounds every attempt, terminates/reaps the child, verifies each removal,
   and fails unless overlay, module, device, installed file, GPIO4, clock, and
   protect-count state all return to baseline.
6. The initial evidence directory could be reused, the log was appendable, and
   its digest was taken while still changing. The runner now requires a new
   evidence directory, closes and waits for the log writer, and hashes the
   stable command ledger with every other raw evidence file.
7. Warning-or-higher kernel messages were captured but not gated. A dedicated
   classifier now rejects severe fault signatures and accepts only the exact
   expected out-of-tree, pin-conflict, missing-pinctrl, and missing-DMA
   diagnostics; every other warning or error fails the run.
8. The target matrix did not observe rate-protection ownership. Every safety
   assertion now requires exact prepare, enable, and protect counts: protect is
   one only while the production instance is bound and zero after every
   unwind, unbind, unload, failed probe, and final cleanup.
9. The installed and loaded artifact was not cryptographically tied to the
   tested build. The runner now checks the `modprobe` selected path, compares
   installed bytes, validates the live module version, and records hashes for
   both the signed test artifact and installed copy.
10. The simulated update negative initially called Make directly. It now
    sources the exact `dkms.conf` recipe with a missing kernel-header identity,
    requires a bounded nonzero result and no candidate install, then proves the
    unchanged running-kernel artifact can still bind safely. Full DKMS staging
    remains a later packaging workflow because `dkms` is absent on this exact
    target.
11. UAPI and runtime DT identities were printed but not checked. The target
    client now machine-validates route, compatibility ceiling/reason,
    capabilities, module/build/compatibility IDs, acquisition exclusion, and
    release. A separate DT checker resolves and validates the clock and DMA
    providers, GPCLK0 ID, DMA request, common RP1 parent, resource containment,
    translated provider resource, divider target, and successful map implied
    by endpoint registration.
12. Target mutations and expected failures lacked consistent bounds/status
    records. Commands now run with TERM/KILL deadlines; sysfs writes use the
    same wrapper; expected failures reject success and timeout statuses; and
    install, unload failure, process kill, and removal are in the ledger.
13. The static gate previously missed a route-property and runner-CLI defect.
    It now requires the route and new target assets, ShellCheck covers the
    target runner, and the UAPI client is compiled with warnings fatal on Linux
    before the separately compiled target copy is used.
14. Independent review found DMA provider identity and resource evidence were
    incomplete. The driver now rejects any DMA provider other than the exact
    allowlisted RP1 DMA identity/request under the same RP1 parent as the clock
    provider; target evidence independently resolves providers and records the
    translated resource, relative divider target, and successful mapped bind.
15. The first strict dmesg classifier used word boundaries that could miss
    severe signatures ending in punctuation. The expression is corrected, and
    deterministic offline fixtures now prove expected messages pass while
    `WARNING`, `BUG`, `Oops`, `Call Trace`, and generic module cleanup errors
    fail even when they also resemble an allowed pin-conflict message.
16. The runner initially logged PASS before evidence hashing and signing-key
    cleanup. It now removes and verifies the disposable work directory while
    the cleanup trap remains armed, closes and waits for the ledger writer,
    generates and verifies the evidence manifest, and emits PASS only after
    all of those operations succeed.
17. The first corrected target preflight found that strict C11 did not expose
    Linux `O_CLOEXEC` to the target UAPI client. The client now defines the
    required GNU feature-test profile before system headers, and both the Linux
    offline suite and the runner's independent warnings-fatal compile must pass
    before module build or mutation continues.
18. The next target preflight built the Linux client and module cleanly but
    found that Raspberry Pi's split header packages keep DT bindings under the
    version-matched `rpt-common-rpi` tree rather than the architecture build
    tree. The runner now derives that exact common-header identity from the
    running `rpt-rpi-2712` release, validates both required RP1 bindings and
    their package ownership, and compiles overlays only from that include root.
19. The next target preflight compiled every overlay but found that the runner
    invoked a non-executable Python module checker directly. All target Python
    assets are now invoked through the recorded `python3` interpreter, so file
    mode cannot bypass their required checks. The related review also tightened
    finding 18: both RP1 binding paths must resolve to the exact derived common
    header package, not merely exist.
20. The first production-overlay bind failed closed with a DMA-mask overflow
    and kernel warning because `dma_map_resource()` used the consumer platform
    device instead of the allocated RP1 DMA controller device. Mapping and
    unmapping now use `dma_chan->device->dev`, matching the proven DMAengine
    translation boundary; static checks prevent regression. The same diagnosis
    found that this `dmesg` rejects ISO timestamps, so the runner now captures
    all-message and warning-level boot-stable line cursors before the run and
    slices only newly appended diagnostics.
21. After the DMA correction, every target lifecycle assertion passed through
    final cleanup, but the strict diagnostic classifier rejected the exact RP1
    pinctrl conflict sequence. The classifier now allowlists only those exact
    fixture-specific messages, and a dedicated empty-default-state fixture
    isolates a real DMA-channel conflict while the production instance owns
    the request. Independent review also rejected line counts as wrap-sensitive
    dmesg cursors: the runner now captures full baseline/final snapshots and
    fails unless each baseline is an exact intact prefix before extracting its
    suffix.
22. The first duplicate-DMA fixture run proved that DMAengine does not make
    the peripheral request ID exclusive: a second identical endpoint reached
    duplicate misc-device registration and triggered a kernel warning. The
    driver now claims the exact composite GPCLK0/GPIO4/DMA-request endpoint
    before acquiring resources and releases that claim on every probe unwind
    and remove path. The fixture must fail with `-EBUSY` at that explicit
    ownership gate, without a misc/sysfs warning. The same run showed that a
    broad GPIO4 diagnostic allowlist and an assumed consumer suffix were not
    exact. The classifier now accepts only the observed four-line conflict
    sequence and rejects unrelated near matches. Full dmesg baselines and
    finals are retained in the hashed evidence so prefix proof is auditable.
23. The corrected duplicate-endpoint target run rejected the second endpoint
    at the explicit ownership gate with `-EBUSY`, preserved the production
    endpoint and safe state, and emitted no kernel warning or call trace. The
    strict classifier then rejected the kernel's companion platform-probe
    summary because it had not been listed. That exact fixture-specific
    `failed with error -16` line is now required exactly once alongside the
    ownership diagnostic; variants and unrelated failures remain rejected.
24. Independent review found that publishing the composite endpoint as free
    with plain `atomic_set()` was not release-ordered after DMA, pinctrl, and
    clock teardown on ARM64. The release path now uses
    `atomic_set_release()`, paired with the successful ordered compare/exchange
    claim, so a later owner cannot enter acquisition before prior resource
    teardown is visible. A static gate prevents regression to an unordered
    release.
25. The first ordered-release target rerun completed every lifecycle and
    cleanup assertion but exposed an over-tightened classifier mistake: kernel
    diagnostics identify fixture DT node names, which omit the overlay
    filename's `gpio4` component. The missing-active and bad-DMA patterns now
    match the exact observed DT node identities while retaining exact errno,
    message, and exactly-once requirements.
26. The first downloaded successful evidence bundle exposed that its inner
    manifest recorded absolute target paths. It verified in place on `wspr5`
    but was not independently relocatable. Manifest generation now changes
    into the evidence directory, hashes relative `./` names, and verifies that
    same portable manifest before PASS. The full matrix must be repeated
    because the runner is part of the hashed source identity.
27. Independent review of the superseded bundle found that
    `production-dt.txt` was empty because sysfs exposes `of_node` as a symlink
    and the evidence walk did not follow it. The runner now uses `find -L` and
    requires the retained raw DT property dump to be nonempty. The separate
    machine validator remains mandatory; neither artifact substitutes for the
    other.
28. Final review found that the successful path asserted GPIO/clock counts but
    relied on the failure trap for overlay, module, device, installed-file, and
    client-process absence. A shared absence assertion now runs both on the
    explicit success path and in trap cleanup, with its complete state recorded
    in the immutable ledger.
29. The process holder was previously launched directly and its wait status
    suppressed. The ledger now records the exact holder command, PID,
    post-acquisition marker/lease readiness, kill command, and required wait
    status 137. Descriptor open, rejected new-open, and close actions also have
    explicit timestamped status records.
30. Review corrected an inaccurate bad-DMA fixture comment. Missing `dmas` is
    rejected during exact DT identity validation before resource acquisition;
    it proves fail-closed unknown DMA identity, not DMA-acquisition unwind. The
    missing-active fixture proves target unwind after clock acquisition, while
    deterministic offline fault tests retain unavailable-DMA acquisition and
    reverse-unwind coverage. No unsafe target DMA-provider disruption is
    introduced merely to force that branch.
31. The simulated kernel-update failure sourced the correct recipe but ran it
    outside the source directory, so Make failed for a missing Makefile rather
    than the nonexistent header identity. The child now changes to the exact
    source directory, executes `MAKE[0]`, requires diagnostics naming
    `/usr/src/linux-headers-phase2e-missing`, and uses a reserved status that
    the expected-failure wrapper rejects if provenance validation fails.
