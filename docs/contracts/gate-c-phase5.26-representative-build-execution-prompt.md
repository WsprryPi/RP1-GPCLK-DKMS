<!-- SPDX-License-Identifier: MIT -->

# Gate C Phase 5.26 exact representative-build execution prompt

## Objective and authorization

Under the operator's explicit authorization of 2026-08-16, perform one exact,
disposable, build-only representative qualification of frozen Phase 5.26 on
`wspr5`. Establish no claim above `Compatible-unqualified` and
`liveEligible: false`.

## Frozen candidate

- Release: `0.0.0-phase5.26`
- Source commit: `9f009240eecd55940d53d6f13cb9567aa76cd4ce`
- Archive: `rp1-gpclk-dkms-0.0.0-phase5.26.tar.gz`
- Archive SHA-256:
  `f43422342fc03c402eb0602949cc317aea239defc6544534ea98bc40d2c505bc`
- UAPI SHA-256:
  `1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`
- GPIO4 DTBO SHA-256:
  `c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`
- GPIO20 DTBO SHA-256:
  `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`
- Compatibility-manifest SHA-256:
  `4444431d7706a1cb77005d969d3665b238b6e935cd585e281b2b0ad9017f6331`

## Required target identity

Fail closed unless immediate read-only preflight confirms `wspr5`, Raspberry Pi
5 Model B Rev 1.0, revision `c04170`, `aarch64`, stock kernel
`6.18.34+rpt-rpi-2712`, matching installed headers, Debian GCC 14.2.0, header
build-tree `.config` SHA-256
`2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801`,
and `Module.symvers` SHA-256
`681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`.
Record the distinct `/boot/config-*` digest without substituting it for the
build-tree identity. Also require no loaded `rp1_gpclk_dkms` module, no
`/dev/rp1-gpclk` endpoint, no active RP1 GPCLK overlay, and no test-owned DKMS
registration.

Identity drift, unexpected residue, unavailable headers or tools, a changed
kernel configuration or `Module.symvers`, unsafe paths, or unexplained build
failure stops the operation without cleanup beyond exact newly created
test-owned paths.

## Permitted operation

1. Reproduce and independently validate the exact frozen archive locally.
2. Transfer only that archive and a reviewed, bounded build driver to a new
   user-owned target staging directory.
3. Verify the archive hash on target before extraction.
4. Extract into a new disposable user-owned directory with one exact archive
   root and reject links, special files, absolute paths, traversal, or foreign
   bytes.
5. Build the module directly against
   `/lib/modules/6.18.34+rpt-rpi-2712/build` without DKMS registration.
6. Compile the busy injector and UAPI probe from frozen source, but never
   execute them.
7. Record bounded commands, timestamps, target identity, package/header and
   compiler identities, kernel configuration and `Module.symvers` hashes,
   archive/UAPI/module/helper hashes, module version, vermagic, diagnostics,
   unresolved-symbol and modpost results, and final runtime state.
8. Seal a new immutable evidence directory and relative checksum manifest,
   retrieve and independently verify it locally, then remove only the new
   archive staging, disposable build directory, and build driver.

## Prohibitions

Do not install packages; invoke DKMS add/build/install/remove; copy into
`/usr/src`; sign; enroll keys; load, bind, unbind, or unload a module; apply an
overlay; change services, boot configuration, kernels, headers, signing policy,
or system configuration; reboot; access GPIO, pinctrl, GPCLK, clocks, or DMA;
execute either helper; operate Si5351 or SDRplay; connect an antenna; transmit;
perform RF work; use `/dev/mem`; select a fallback; or touch preserved Phase
5.24/5.25 evidence.

## Evidence and exit criteria

The build passes only if all exact identities match, compilation exits zero,
diagnostic policy passes, helper binaries are compiled but not executed, the
final runtime state remains unchanged, the evidence manifest verifies both on
target and after retrieval, and all disposable inputs are removed. Conduct a
separate adversarial assessment before accepting the evidence.

After acceptance, commit and push only the new authorization prompt,
representative-build evidence, manifest, tests, candidate-status update, and
adversarial assessment. Stop before route-decision or lifecycle-control-set
construction and before all Gate D target administration.
