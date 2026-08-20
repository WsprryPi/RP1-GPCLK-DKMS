<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 final lifecycle-control package recapture authorization prompt

## Objective

Authorize one bounded read-only recapture of the exact inactive Phase 5.53
product installation on `wspr5` and, only if it matches the recorded install
attestation and safety state, construct and validate a durable lifecycle-control
package offline from the final artifact closures and the newly captured target
closure.

## Fixed artifact identities

- Product source: `4e7a64a0ca353d2fcab6e25891f5254746e2b91a`.
- Product archive SHA-256:
  `032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76`.
- Qualification source: `e074c9dc01244f7efb73b95a8007bca3625b9c85`.
- Qualification archive SHA-256:
  `31dd96079930d4c77788aea506cd0fa549d2ec101c1cf93ab3d5b392e76caaf5`.
- Installed successor ledger SHA-256:
  `d4fe02f8d66ac298f2076b37be297097f392095904cc3809717713cd01a14f8d`.
- Installed successor closure SHA-256:
  `414653b869feb38b8151a68c808d5fc7d8d4693410692078f59670d4a9aa0d5e`.
- Target kernel: `6.18.34+rpt-rpi-2712`.

## Why recapture is required

The durable install attestation records the final ledger and closure hashes,
72 owned files, 15 owned directories, DKMS installed state, and inactive
safety state. It does not retain the ledger bytes or complete 72-file path
inventory. The existing Phase 5.53 generator instead binds the retired product,
qualification archive, authorization, Phase 5.52 ledger, and 28-path package
inventory. Those controls must remain historical and may not be patched or
treated as the new package.

## Authorized work after the exact phrase

1. Verify the repository is clean, synchronized, and at the exact decision
   commit; verify both final archive hashes before target contact.
2. Perform read-only capture on `wspr5` using reviewed snapshot code streamed
   directly to privileged Python. Do not install the capture code.
3. Capture the complete terminal ledger bytes and hash; canonical owned-file,
   owned-directory, replacement, DKMS, installed module, kernel/header,
   service, overlay, endpoint, boot, signing, physical-safety, and residue
   state; and every path identity required by the final product closure.
4. Require the recorded ledger and closure hashes, kernel, 72 owned files, 15
   directories, zero replacements, installed DKMS version, both inactive DTBO
   hashes, absent qualification tooling, absent module and endpoint, no applied
   or selected overlay, inactive controlled services, no transfer residue,
   disconnected antenna, unused SDR, and disconnected/unused Si5351. Any
   mismatch exhausts authorization without generation.
5. Require two canonical captures to be byte-identical. Persist only the
   reviewed, non-secret evidence needed for reproducibility.
6. Reconstruct every path-bearing consumer from the product archive,
   qualification archive, and new capture. Use a new namespace and files;
   preserve all historical Phase 5.53 controls unchanged.
7. Set `approved=false`, `targetExecutionApproved=false`, and
   `executionReady=false`. This authorization does not flow into the generated
   package.
8. Generate the complete control package twice, require byte identity, validate
   all hashes and paths independently, reconstruct its sealed root from package
   bytes alone, and exercise all attempts against the offline fake system.
9. Run focused regressions, documentation links, whitespace checks, and an
   adversarial review. Commit and push only attributable offline controls and
   evidence, then stop for a separate staging/pre-root authorization.

## Prohibited work

Do not transfer or stage qualification inputs on the target; create a target
qualification root; perform a pre-root transition; install, remove, load,
bind, or unload a module; apply an overlay; modify boot or service state;
reboot; access GPIO; enable a clock; submit DMA; transmit; or produce RF. Do
not execute a lifecycle attempt.

## Exact authorization phrase

> I explicitly authorize the exact Phase 5.53 final lifecycle-control package
> recapture and offline construction slice bound to product archive
> 032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76,
> qualification archive
> 31dd96079930d4c77788aea506cd0fa549d2ec101c1cf93ab3d5b392e76caaf5,
> installed ledger
> d4fe02f8d66ac298f2076b37be297097f392095904cc3809717713cd01a14f8d,
> and installed closure
> 414653b869feb38b8151a68c808d5fc7d8d4693410692078f59670d4a9aa0d5e,
> including exactly two byte-identical read-only captures and, only if they
> match, offline reconstruction, deterministic generation, fake-system
> exercise, review, commit, and push of new unauthorized controls. I do not
> authorize target staging, a pre-root transition, any lifecycle attempt,
> module or overlay activity, reboot, GPIO/clock/DMA activity, transmission, or
> RF.

Until that exact authorization is supplied, do not contact `wspr5` or generate
controls that claim the missing current target closure.
