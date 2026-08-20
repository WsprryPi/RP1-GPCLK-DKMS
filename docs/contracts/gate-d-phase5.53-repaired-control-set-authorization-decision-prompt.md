<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 repaired control-set authorization decision prompt

## Objective

Permit the operator to authorize only a final read-only preauthorization
recapture and, if it is byte-identical to the canonical snapshot, regeneration
and commit of the repaired Phase 5.53 offline controls. This prompt does not
authorize target staging, the authenticated pre-root transition, or any Gate D
lifecycle attempt.

## Exact repaired identities

- repaired-control commit:
  `dff45f11720496a983327131972f7d78ca66ff70`;
- execution-instance SHA-256:
  `2b6dc7e2d81711c2179aec8a73bd5e9d54e9090cd82c1a7195f0272a35ed0890`;
- schema-6 pre-root envelope SHA-256:
  `866c433bbf25ef71953fd79fb7f82ff103be18a62b1af8b4df57daaca9b4b8c2`;
- unchanged 38-attempt index SHA-256:
  `3a6a6047dc8e3ca5c77488a5029bb2165f5b9e71bf32fdc94ec60dcf15ec15e2`;
- repaired 46-file control-tree SHA-256:
  `d484fe0ff19bdc2de2e1b78c8269f05ac278587b10bf0ca042f4eb9398af9b7c`;
- canonical snapshot SHA-256:
  `df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7`;
- product archive SHA-256:
  `ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549`;
- qualification archive SHA-256:
  `d931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0`;
- predecessor inventory SHA-256:
  `17220ae534936e55fc1710edcd8cebff88add93adb82bd607e020714569a175d`;
- qualification-install identity SHA-256:
  `c4bdf3e066527941e5762229d0162b738bea542ec8d47a2cdfda0e66ef7a0ebb`;
- successor release-input inventory SHA-256:
  `b3ae7d71aa1eb8881450b068f9c3525ecf33925ab797419c735b9f4f5aca18cb`.

The superseded envelope
`aa07ee829ee01d0bdcdfbc3c0882b2ddd582c9f48c5e8b69253b315522a47e9c`
and every authorization bound to it remain retired and cannot carry forward.

## Repaired path closure

The envelope contains 64 declared inputs, eight release inputs, 55 transition
files, 22 installed tools, 28 predecessor package paths, and 28 successor
package paths. `stagedExecutor` and `preRootModule` are bound to their exact
`control-set/scripts/` inputs. The administrator remains bound to the extracted
54-file product archive. The 118-path offline split-staging rehearsal executed
the exact archived pre-root entry point successfully.

## Authorized work if the exact phrase is supplied

1. Stream the exact reviewed read-only snapshot tool into privileged Python on
   `wspr5` twice without creating a target tool file.
2. Require both 7,083-byte captures to be byte-identical to each other and the
   canonical snapshot. Require the inactive baseline, exact predecessor paths,
   terminal ledger, absent Phase 5.53 staging/root/journal/attempt paths, and
   declared physical safety state to remain unchanged.
3. If and only if every comparison passes, regenerate the repaired controls
   deterministically with authorization recorded for this exact control set,
   update only transitively affected authorization evidence and hashes, run the
   complete offline suite and adversarial review, and commit and push those
   offline changes.
4. Stop before target staging. Do not transfer files, create target paths,
   invoke the administrator or pre-root executor, or begin lifecycle attempt 1.

Any mismatch retires this decision without regeneration. Product and
qualification archive bytes must remain unchanged. GPIO output, active
pinctrl, clock enablement, DMA, Si5351 or SDR operation, antenna connection,
transmission, RF, `/dev/mem`, forced removal, general upgrade, and unreviewed
boot mutation are prohibited.

## Exact authorization phrase

> I explicitly authorize the exact repaired Phase 5.53 control set at commit
> dff45f11720496a983327131972f7d78ca66ff70, beginning with the bounded
> read-only byte-identical preauthorization recapture and, only if it matches,
> regeneration and commit of the repaired authorized offline controls bound to
> envelope 866c433bbf25ef71953fd79fb7f82ff103be18a62b1af8b4df57daaca9b4b8c2.
> I do not yet authorize target staging, the pre-root transition, any Gate D
> lifecycle attempt, GPIO/clock/DMA activity, transmission, or RF.

This decision prompt is non-authorizing. Do not contact the target or alter the
repaired controls until the operator supplies that exact phrase.
