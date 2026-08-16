<!-- SPDX-License-Identifier: MIT -->

# Phase 5.39 authorized execution adversarial assessment

Status: failed closed during staged-input verification; no pre-root transition
or lifecycle attempt began

The operator authorized the sealed Phase 5.39 control set at commit
`fde402544d5bdb917c8f5daf537d7dd0742af88b`. The authorization-bound bytes were
committed and pushed as
`45a824f` before target staging. The authorized execution-instance SHA-256 was
`fd73346bb38ba4ebcb2c8ef6b616d4d08b1c045b6d1761fd3f843a82e5871917`,
and the pre-root envelope SHA-256 was
`4019430a96fc0c48b6ae4435aa0fd764cfae45ff2b04cd02b5ee47c48000626d`.

Read-only preflight on `wspr5` passed before staging. The target was running
stock kernel `6.18.34+rpt-rpi-2712` on `aarch64`, with no loaded module, device
endpoint, active overlay, Phase 5.39 DKMS entry, Phase 5.39 pre-root journal,
input directory, or qualification root. All 28 typed predecessor package paths
matched their exact type, regular-file hash or symlink target, mode, owner, and
group. The recovered Phase 5.37 canonical ledger remained root-owned mode
`0600`, inactive and recovery-complete, with SHA-256
`24af8111eaa7e9f0c5084dd39063160a5188195a73667b3fcbf115c3c4ea64cf`.
The preserved Phase 5.36 and Phase 5.34 archives also retained their sealed
hashes and root-owned mode `0400`.

After exact staging of the representative-build artifacts and all 58 control
transition files, the required 67-file closure check stopped on four release
sidecar mismatches:

| Path | Sealed SHA-256 | Staged Phase 5.39 SHA-256 |
| --- | --- | --- |
| `PROVENANCE.json` | `78de6dbbd14787a7baf5099acacd87615509fe3b34b393e8e8951b6d64da9747` | `8ada380c2950632affe4b7e92d909fc592a5d43653c39df089d173d4deb4f89e` |
| `SHA256SUMS` | `55a717972c56b7f132c05f2876072eefa98737497f75dff807438051dfd34245` | `d2582c90c862e18efa84791b97793ede956f73ad6f8be61156a50bd3d1218064` |
| `release-metadata.json` | `789487a958ff160a503349d20a7a5f2757e1dcc525f9b114e23c766dab80e196` | `e1fbf1ce9d95482bebce8d4c18dc9722213f6abf9d9bb47ce6a431f62af52fff` |
| `rp1-gpclk-compatibility-manifest.json` | `6c12ee6997b9f0f9d6ed40da5c276a5a8223da6019dc1fcadba10a39fc395359` | `69365d1f2924ea619f71817ecf0624f96ee172a3ee6c59de614aab1d89b54a38` |

The source archive and both DTBOs matched their sealed hashes. The defect is in
the deterministic generator: it transformed the Phase 5.37 control documents
without rebinding these four generated release-sidecar identities to the exact
Phase 5.39 representative-build bytes. Offline closure validation proved
internal agreement with the stale values but did not compare them with the
actual representative-build sidecars.

The exact Phase 5.39 staging directory was removed after confirming that no
qualification root or pre-root journal existed. Final checks found no loaded
module, device endpoint, or overlay. No DKMS administration, service change,
package transition, GPIO access, clock enablement, DMA submission, Si5351
operation, SDR or transmitter operation, reboot, transmission, or RF occurred.

This result supplies no lifecycle or qualification evidence. The authorization
must not be reused. The next control-set successor must derive and bind every
release-input hash from the exact representative-build directory, add a test
that compares every envelope release input with those actual artifacts, repeat
deterministic construction and adversarial validation, and receive fresh
authorization before target staging or execution.
