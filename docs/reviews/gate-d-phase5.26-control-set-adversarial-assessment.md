<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.26 control-set adversarial assessment

Status: offline software and control-contract review passed; fresh target
authorization intentionally absent

The Phase 5.26 control set binds frozen source commit
`9f009240eecd55940d53d6f13cb9567aa76cd4ce`, archive SHA-256
`f43422342fc03c402eb0602949cc317aea239defc6544534ea98bc40d2c505bc`,
the exact accepted representative-build manifest, compatibility sidecars,
packaged tool graph, target-built helper identities, and separate GPIO4 and
GPIO20 decisions. Both routes remain `Compatible-unqualified` and
`liveEligible: false`; no build evidence is promoted into live-output,
transmission, RF, calibrated-output, or consuming-application qualification.

The schema-2 pre-root envelope authenticates seven release roles in one exact
release directory and 58 unique transition source/destination identities. The
transition covers the qualification identity, representative-build manifest,
bootstrap, route decision, target plan, execution instance, attempt index, all
38 attempts, schemas, permanent validators and executors, imported Python
modules, and helper sources. The root marker SHA-256 is
`3a0165ea5084f8cc01c4fa2ed37760d266be662e22f08df508c624d94cbd8f39`;
the envelope SHA-256 is
`595d6e8c2c3e0538ad3f51ace2ea6977b6cb514d1dbc9374eb9db37a4725024a`.

All 38 attempt documents regenerate byte-for-byte from the permanent
generator. Operation IDs, evidence directories, journals, and staging
directories are unique. Fake execution covers the 15 durable interruption
checkpoints, four busy-state cases, current and prior stock kernels, signing,
stale and corrupted inputs, build failure, removal, reinstall, recovery, and
service restoration. Every fake attempt completed, sealed evidence, removed
attempt-owned residue, restored services, and kept live output false. Five
rows whose environmental prerequisites are unavailable remain explicitly
`deferred-environmental` rather than fabricated.

Adversarial mutations of release-role membership, release directories,
transition hashes, destinations, input paths, and output-disabled safety state
were rejected. Validation also confirms exact candidate and representative-
build identities, closed tooling and import graphs, 38-attempt cardinality,
route-specific non-live decisions, and the complete qualification-root trust
transition. No identity substitution, historical Phase 5.25 mutation, unsafe
path, unbound dependency, or claim expansion remains. Staged-diff review found
and corrected one status-metadata error: `reuseProhibited` is the complete
list of Phase 5.25 artifacts that Phase 5.26 must not reuse, not a checklist of
unfinished Phase 5.26 work.

The topology wording is correct: Si5351 is a separate I2C-controlled RF output
path, while GPIO4 and GPIO20 are reserved routes for this DKMS module. The
`si5351Disconnected` invariant describes disabled/unkeyed RF-path isolation;
it does not assert a Si5351-to-GPIO connection.

The execution instance deliberately retains `targetExecutionApproved: false`
and `executionReady: false`. Readiness validation therefore fails closed with
`fresh target-execution authorization is required`. No target was contacted,
and no package, DKMS, module, overlay, service, boot, reboot, GPIO, GPCLK,
clock, DMA, helper, Si5351, SDR, antenna, transmission, or RF action occurred.
