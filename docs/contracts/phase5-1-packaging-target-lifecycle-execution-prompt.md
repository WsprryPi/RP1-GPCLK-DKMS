<!-- SPDX-License-Identifier: MIT -->

# Phase 5.1 packaging and representative target lifecycle execution prompt

## Mission and exit condition

Act as the packaging implementer, representative-target lifecycle operator,
evidence custodian, and adversarial reviewer for
`WsprryPi/RP1-GPCLK-DKMS`. Deliver a reproducible, checksummed source archive;
DKMS, signing, overlay, diagnostic, rollback, recovery, and complete-removal
tooling; strict compatibility metadata; deterministic offline and simulated
failure tests; and one recorded representative target lifecycle matrix.

Phase 5.1 closes only when the offline suite passes twice, the archive rebuilds
byte-for-byte, every target lifecycle row has its expected result and cleanup,
the target is restored to its recorded baseline, and a separate adversarial
review has no unresolved objective finding. A successful build, signature, or
installation never exceeds `Compatible-unqualified` and never enables output.

## Authority

The current Phase 5.1 authorization covers two separate classes of work:

1. **Offline implementation:** packaging, scripts, documentation, manifests,
   static tests, archive generation, and simulated failure tests.
2. **Representative target lifecycle testing:** DKMS prerequisite installation,
   registration, signing, build, installation, output-disabled overlay handling,
   module load/bind/query/unbind/unload, upgrade, downgrade, rollback, recovery,
   removal, and exact final-state verification.

Target lifecycle work remains clock/output-disabled. This prompt does not
authorize active pinctrl selection, common-clock enablement, DMA submission,
GPIO output, transmitter keying, antenna connection, or RF transmission. If a
lifecycle check appears to require live output, stop and obtain a new, exact
authorization; do not infer it from Phase 4 evidence.

## Governing contracts and exact starting point

Follow `AGENTS.md`, the module engineering contract, phased plan, frozen UAPI
v1 contract and identity, compatibility schema, current decisions, and prior
Phase 2E/3B/4 evidence. Preserve repository boundaries. Inspect Git and target
state before mutation and preserve unrelated work.

Use only stock Raspberry Pi kernels and exported kernel APIs. Persistent
prohibitions are absolute:

- no custom kernel or replacement of stock `clk-rp1`;
- no `/dev/mem`, raw-userspace-MMIO, fixed-physical-address, or private-symbol
  production fallback;
- no automatic fallback to another physical transmitter;
- no arbitrary GPIO routing; and
- no weakening or wildcarding an unknown kernel, DT, firmware, signing,
  resource, route, UAPI, artifact, cleanup, or recovery identity merely to make
  installation succeed.

## Offline deliverables

Implement the smallest maintainable release/lifecycle surface that provides:

1. A release version used consistently by module metadata and `dkms.conf`.
2. A deterministic source archive with one versioned top-level directory,
   normalized ownership, permissions, order, timestamps, and gzip metadata.
   Exclude Git state, build products, caches, evidence captures, and secrets.
3. A checksum/provenance manifest covering the archive, canonical UAPI,
   overlays, compatibility manifest, source commit, dirty-state indicator,
   tool version, and generation command. Refuse a release archive from a dirty
   tree unless an explicit development-only override marks it non-release.
4. A deny-by-default release compatibility manifest. Unknown identities remain
   `Unavailable`; lifecycle evidence may create only exact
   `Compatible-unqualified` rows with `liveEligible=false`.
5. Root-facing lifecycle tooling with explicit actions for preflight,
   register/build/sign/install, route overlay install/enable/disable, load,
   clock-disabled query, unload, unregister, rollback, recovery, removal, and
   status. Commands must be idempotent where safe, log exact actions, validate
   package/version/path/route, and refuse symlinks or unexpected ownership.
6. A signing interface that uses an administrator-supplied private key and
   certificate, never archives or logs private material, validates the signed
   artifact, and fails closed when enforcement requires a signature. Document
   that signing proves provenance/load eligibility only.
7. Overlay handling limited to the two packaged allowlisted overlays. Boot
   configuration changes need explicit action, exact markers, duplicate and
   conflict rejection, atomic backup/replacement, rollback, and no reboot by
   default. Runtime overlay handling may be used only when supported and must
   reject removal while bound or busy.
8. Upgrade/downgrade and rollback semantics that preserve the prior known
   package until the successor passes build, signing, install, output-disabled
   load/query, and cleanup. Failure restores only tool-owned state and never
   changes compatibility qualification.
9. Complete removal that removes only this package/version, module, overlays,
   marked configuration, generated state, and tool-owned backups after proving
   absence. Never remove another DKMS package, key, kernel, overlay, boot entry,
   or administrator file.
10. Operator documentation for prerequisites, Secure Boot/signing, install,
    status, output-disabled verification, updates, downgrade, rollback,
    recovery, removal, warnings, evidence capture, and exact non-goals.

Add static and simulated tests for archive reproducibility and contents;
checksums and tampering; invalid versions/routes/paths; unknown identities;
missing DKMS, headers, tools, key, certificate, overlay support, and signing
enforcement; DKMS add/build/install/uninstall/remove failures; signing and
verification failures; overlay conflict and partial write; load/query/unload
failure; upgrade/downgrade interruption; rollback failure; stale state;
cleanup failure; idempotence; and protection of non-owned files. Mocks must
never call real DKMS, modprobe, boot configuration, GPIO, clock, DMA, or RF.

## Representative target procedure

Before each mutating target sequence capture hostname, model/revision, kernel,
architecture, boot and DT identities, compiler, headers, DKMS version, signing
policy, loaded modules, overlays, boot configuration, package state, taint,
relevant dmesg baseline, source/archive/UAPI/overlay hashes, route, and current
output gate. Stop on an unexplained delta or unknown identity.

Use a fresh evidence directory and record commands, timestamps, exit status,
stdout/stderr, artifact hashes, expected outcome, and cleanup result. Do not
record private key material. Execute the following matrix with
`live_output=false` and a single allowlisted route at a time:

1. Install or verify the stock-distribution DKMS prerequisite and exact running
   kernel headers without replacing the kernel.
2. Verify deterministic archive and checksum/provenance manifest on target.
3. Register, build, optionally sign according to target policy, install, and
   validate vermagic, signature metadata, module/UAPI/version identity, and
   absence of output eligibility.
4. Install each packaged overlay artifact and validate its hash. Exercise only
   reviewed output-disabled overlay handling; do not enable active output.
5. Load/bind/query/release/unbind/unload with the immutable live-output gate
   false. Prove no DMA activity, zero clock prepare/enable deltas, safe pins,
   restrictive device node, clean terminal state, and bounded removal.
6. Inject a signing rejection and DKMS build/install failure without weakening
   policy; prove `Unavailable`, no fallback, and no residue.
7. Exercise an upgrade to a distinct development package version, downgrade to
   the prior version, induced successor failure with automatic rollback, and
   recovery from interrupted/stale tool-owned state. Never treat version order
   as compatibility qualification.
8. Uninstall and unregister every test version, remove only test-owned overlay
   and marked configuration state, and prove repeated removal is safe.
9. Compare final kernel, boot, module, DKMS, overlay, config, device-node,
   filesystem, taint, and dmesg state with baseline. Retain only the approved
   evidence bundle; no module or overlay may remain active.

No reboot is implicit. If boot-time overlay verification genuinely requires a
reboot, stop and obtain explicit reboot authorization with a recovery plan.

## Evidence and claims

Record raw and summarized evidence with SHA-256 checksums. The result must say
what was built, signed, registered, installed, loaded, queried, rolled back,
recovered, and removed; identify skipped checks; and distinguish simulated
failure evidence from real target evidence. Lifecycle success establishes only
the exact target/package identity as `Compatible-unqualified` with live output
disabled. It does not qualify GPIO behavior, timing, coexistence, modes,
transmission, RF, another kernel, another route, or automatic application use.

## Required adversarial loop

After implementation and again after target execution, conduct a separate
assessment attempting to falsify archive reproducibility and completeness;
version/UAPI/manifest consistency; provenance and secret exclusion; shell and
privilege safety; symlink/path/ownership protections; signing enforcement;
overlay/boot atomicity; DKMS failure cleanup; upgrade/downgrade/rollback;
recovery from every interruption point; complete removal; target baseline
restoration; deny-by-default compatibility; restrictive permissions; and all
non-goals.

For every finding, amend this prompt if the requirement was missing, implement
the correction, rerun all affected offline and target rows, and repeat the
assessment. Exit only with no unresolved objective findings. Then run the
complete offline suite twice, documentation/link/SPDX/whitespace checks,
archive reproducibility check, and final Git and target-state audit. Commit and
push the cohesive reviewed result when warranted; do not publish a release or
change issue lifecycle unless separately authorized.
