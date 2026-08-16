<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.25 control-set adversarial assessment

Status: offline software and control-contract review passed; fresh target
authorization intentionally absent

The Phase 5.25 release lifecycle qualification control set binds frozen source
commit `d9f8fd8b17f1c2ee9324704c6b6630dfccfb5e4e`, archive SHA-256
`e615750897009b79d0ead1e3bbf4133e0c4d5c157cc259d513a76ad65bd993e4`,
the exact Phase 5.25 representative-build manifest, and separate GPIO4 and
GPIO20 decisions. Both routes remain `Compatible-unqualified` and
`liveEligible: false`. The route-neutral build is not used as route-specific
GPIO, calibrated-output, lifecycle, transmission, SDR, RF, publication, or
consuming-application evidence.

The schema-2 pre-root envelope contains exactly seven administrator release
roles: archive, GPIO4 DTBO, GPIO20 DTBO, compatibility manifest, provenance,
release metadata, and `SHA256SUMS`. All share one release directory, have exact
path and byte identities, and are also members of the envelope's authenticated
input graph. The permanent pre-root validator independently enforces closed
role membership, directory identity, sidecar filenames, and transitive
`SHA256SUMS` membership before administrator invocation.

The root transition authenticates 58 unique source and destination identities:
the qualification identity, representative-build manifest, bootstrap, matrix,
route decision, target plan, execution instance, exact attempt index, all 38
attempts, published schemas, permanent validators/executors, and the complete
imported Python and target-helper source graph. The installed command and
module identities agree with the representative target-built helper hashes.
No imported module is trusted from a checkout after the qualification root is
created.

All 38 attempts regenerate byte-for-byte from the permanent generator. Their
operation IDs, evidence directories, journals, and staging directories are
individually unique. Every structured operation is in the permanent executor's
closed dispatch vocabulary. Stateful fake execution covers all 15 durable
interruption checkpoints, four busy-state cases, success, stale/corrupt input,
removal, reinstall, and recovery behavior. Each fake run seals evidence,
restores services, removes test-owned residue, and keeps live output false.
The five matrix rows requiring environmental conditions unavailable on the
single qualifying Pi remain visibly `deferred-environmental` and are not
fabricated.

Adversarial tests reject missing or duplicated release roles, wrong release
directories, changed hashes, duplicate destinations, substituted input paths,
unsafe path components, symlinks, foreign or partial state, stale checksum
membership, output-enabled state, and recovery ambiguity. Existing pre-root,
residue, qualification-root, installed-import, lifecycle, attempt, and outer-
executor suites exercise recovery before administrator invocation, after
invocation without state, and with exact state; repeated cleanup and
`already-clean`; foreign-byte discovery before deletion; preservation
boundaries; and interruption at each relevant checkpoint.

No blocking shipped-module, packaged-tool, or qualification-test defect was
found during the original offline assessment. One intentional authorization
gate remains: the checked execution instance has
`targetExecutionApproved: false` and `executionReady: false`. Consequently,
`--require-ready` correctly rejects it with `fresh target-execution
authorization is required`. Setting those fields now would misrepresent the
offline-only authority. After fresh exact authorization is received, the
authorization must be bound into the instance, dependent hashes refreshed,
and `--require-ready` rerun before staging or target contact.

Post-review operator correction identified one packaged-document defect. The
Si5351 is a separate I2C-controlled RF output path and is not wired to GPIO4 or
GPIO20; those pins are reserved for the RP1 GPCLK DKMS module. The control
field `si5351Disconnected` means only that the disabled and unkeyed Si5351 RF
output is isolated from the antenna or test-output path. It must never be cited
as evidence of a physical Si5351-to-GPIO connection.

The source runbook and authorization dossier now state the correct topology,
but their corrected bytes are not part of the frozen Phase 5.25 archive. This
is classified as a packaged control-document defect, not a module, UAPI,
helper, schema, or qualification-test defect. Phase 5.25 must not be published
with the stale packaged wording. Under the successor-restraint rule, a later
candidate is required if the corrected packaged documents are to ship; this
assessment does not create or name that successor.

The complete offline suite passed twice after the final control-set assertions.
No Raspberry Pi was contacted. No package, DKMS, module, overlay, service,
boot, kernel, GPIO, GPCLK, DMA, helper, Si5351, SDR, transmission, or RF action
was performed.
