<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.26 offline control-set construction prompt

## Objective and authority

Under the operator's 2026-08-16 authorization, construct and adversarially
review the complete Phase 5.26 output-disabled Gate D control set. This is an
offline repository operation only. It does not authorize target contact or
execution and must retain `targetExecutionApproved: false` and
`executionReady: false`.

## Exact candidate and representative build

- Release: `0.0.0-phase5.26`
- Source commit: `9f009240eecd55940d53d6f13cb9567aa76cd4ce`
- Archive SHA-256:
  `f43422342fc03c402eb0602949cc317aea239defc6544534ea98bc40d2c505bc`
- UAPI SHA-256:
  `1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`
- Compatibility-manifest SHA-256:
  `4444431d7706a1cb77005d969d3665b238b6e935cd585e281b2b0ad9017f6331`
- GPIO4 DTBO SHA-256:
  `c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`
- GPIO20 DTBO SHA-256:
  `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`
- Representative-build module SHA-256:
  `6be0a2602db6442ad88b34879416fce25dc38dcaaa6b1634a2081ea5a80f600f`
- Representative-build evidence manifest SHA-256:
  `1efeff299da529bf4b0801d6cd46ae967b20acfe3e2ae048a7c8883359b47216`

## Required construction

Create new Phase 5.26 identities for the qualification-install document,
GPIO4/GPIO20 route decision, qualification bootstrap, target operation plan,
38-attempt bundle and index, execution instance, qualification-root marker,
and schema-2 pre-root transition envelope. Bind every candidate, release
sidecar, representative-build, packaged tool, installed tool, schema,
control-document, helper-source, and target-built helper identity transitively.

Regenerate every attempt with the permanent generator and execute every one
against only the stateful fake backend. Preserve the five visibly deferred
environmental rows. Both routes remain `Compatible-unqualified` and
`liveEligible: false`; no route evidence may imply live-output, transmission,
or RF qualification.

The Si5351 is a separate I2C-controlled RF output path. GPIO4 and GPIO20 are
reserved administrative routes for this DKMS module. `si5351Disconnected`
describes disabled/unkeyed RF-path isolation and never a Si5351-to-GPIO
connection.

## Safety and non-goals

Do not contact `wspr5`; stage artifacts; invoke `sudo`, DKMS, installers, or
target executors; install, load, bind, unload, or remove a module; apply an
overlay; change services, boot state, kernels, or configuration; reboot;
execute target helpers; access GPIO, pinctrl, GPCLK, clocks, or DMA; operate
Si5351 or SDRplay; connect an antenna; transmit; or perform RF work. Do not
alter historical Phase 5.25 records.

## Validation and exit criteria

Require deterministic regeneration, closed schemas and operation vocabulary,
unique attempt IDs/evidence/journals/staging, exact hash closure, output-
disabled fake execution with sealed evidence and cleanup, rejection of
adversarial mutations, complete offline-suite success twice, documentation and
whitespace checks, and a separate adversarial assessment. Correct every
actionable finding and repeat affected checks.

Commit and push only attributable Phase 5.26 prompt, control-set, validator,
test, status, and review changes. Stop with fresh exact target-execution
authorization still required before any staging or lifecycle operation.
