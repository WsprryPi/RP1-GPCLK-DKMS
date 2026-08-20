<!-- SPDX-License-Identifier: MIT -->

# Phase 2E GPIO4 clock-disabled target evidence

Date: 2026-08-14
Target: `wspr5`
Result: pass; Phase 2 closed for this exact identity only
Compatibility ceiling: `Compatible-unqualified`

## Evidence identity and integrity

- Raspberry Pi 5 Model B Rev 1.0
- stock kernel/headers `6.18.34+rpt-rpi-2712`, Debian package
  `1:6.18.34-1+rpt1`
- boot ID `c9c5b7f4-6a25-4a47-a347-5cffbf8776e7`
- base FDT SHA-256
  `2ec9e0006dc1f48b4e3cc919d6b58bdfe7bebbe6d01e54315809b7df50d0e058`
- compiler GCC 14.2.0 (`Debian 14.2.0-19`)
- evidence archive:
  `/private/tmp/rp1-gpclk-phase2e-evidence-13.tar.gz`
- evidence archive SHA-256:
  `f9f19c5be727ef8da1ea265f529258acffe9d875adca2cd0c8490c9b57aa1cc1`
- unsigned module SHA-256:
  `87882643f63f6e5aa716a95ccd991bcca54e51178d2d039cb8ce0bb643225899`
- signed and installed module SHA-256:
  `a4afa1495572d233c3792fb65b6d7ba3700a00e34934e97719d1c0b302f92b16`
- production overlay SHA-256:
  `7b642f28e88b4f6c8819dd3c3b03dd8092a64c006d81cc7d3739deebb121825b`

The target generated and verified a relative-path `SHA256SUMS` covering the
command ledger, identities, module metadata, raw DT properties, complete dmesg
baselines/finals and extracted deltas, artifact hashes, and source-tree hash
list. The archive was downloaded, extracted into a different directory, and
all inner hashes verified. `production-dt.txt` was nonempty (1,271 bytes).
Every source hash was remapped to the development worktree and verified against
the pre-final-report tree. The only later changes complete this evidence and
review prose; tested implementation, overlay, and runner bytes are unchanged.

## Exact runtime identity

The bound production node machine-validated:

- route GPIO4 and UAPI ABI 1;
- compatibility `Compatible-unqualified`, reason administrator enrollment
  required, capabilities `0x70`;
- module/build/compatibility identifiers `rp1-gpclk-dkms`,
  `0.0.0-phase2e`, and `phase2e-gpio4-clock-disabled`;
- clock provider `raspberrypi,rp1-clocks`, GPCLK0 ID 33;
- provider resource start `0x1f00018000`, size `0x10038`, and derived
  fractional-divider target `0x1f0001817c`;
- DMA provider `snps,axi-dma-1.01a`, request `0x30`, under the same RP1 parent;
  and
- successful DMA resource mapping through the allocated controller endpoint.

## Matrix result

The complete bounded runner passed:

- warnings-fatal module build, all overlays, strict-C11 UAPI client, and the
  complete Linux offline suite;
- local PKCS#7 signing, installed/selected/loaded byte identity, module version,
  and signed metadata;
- production bind with `/dev/rp1-gpclk` mode `0600`, GPIO4 input, GPCLK0
  prepare/enable zero, and exclusive-rate protect count one;
- exact UAPI query, acquire/release, and single-owner conflict;
- pinctrl conflict rejection and duplicate composite-endpoint `-EBUSY`
  rejection without disturbing the production endpoint;
- unload rejection with an open descriptor, safe unbind while that descriptor
  remained closeable, new-open rejection, and successful rebind after close;
- `SIGKILL` of an owning process, automatic descriptor/module-reference and
  lease release, a recorded wait status of 137, reacquisition, unbind, and
  unload;
- missing-active-pinctrl and malformed-DMA DT probe failures with complete
  unwind and no device node;
- the exact `dkms.conf` build recipe failing against a nonexistent header
  identity with diagnostics naming that header path, no installed candidate,
  and known-good recovery; and
- explicit overlay/module/installed-file removal, signing-key/work-directory
  removal, portable evidence hashing, and final safety assertions.

Full and warning-level dmesg baselines remained exact prefixes of their final
snapshots. The extracted nine warning-or-higher lines were exactly the expected
fixture diagnostics: four pin-conflict lines, two duplicate-endpoint lines,
one missing-pinctrl line, and two bad-DMA identity/probe lines. Severe fault
signatures and unclassified diagnostics were absent.

## Signing classification

The exact kernel has `CONFIG_MODULE_SIG` unset. The runner generated a
disposable key, signed the tested module, verified signer/hash metadata, and
loaded the exact signed bytes. Cryptographic rejection is therefore recorded
as not applicable on this identity. A truncated artifact separately failed the
module preflight; that is not represented as a signature-policy test.

## Final state and exclusions

The immutable success ledger and a separate read-only recheck both proved that
after PASS, GPIO4 was input; GPCLK0
prepare/enable/protect counts were `0/0/0`; no overlay was loaded; and the
module, device node, installed test module, signing key, work directory, and
holder process were absent.

No active pinctrl state was selected. No clock was prepared, enabled, or
rate-changed. No DMA descriptor was prepared or submitted. No GPIO output,
transmission, RF, reboot, boot/configuration, service, or product-repository
operation occurred. The result does not qualify GPIO20, timing, live output,
coexistence against direct MMIO, enforced signing, DKMS installation workflow,
APT upgrade/rollback, another kernel/DT/firmware, or WsprryPi product behavior.
