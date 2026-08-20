<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 repaired target-staging and pre-root authorization decision prompt

## Objective

Permit the operator to authorize only the repaired Phase 5.53 pre-attempt
target-staging slice and exactly one authenticated pre-root transition. This
prompt does not itself authorize target contact or mutation, and it does not
authorize lifecycle attempt 1 or any GPIO, clock, DMA, transmission, or RF
activity.

## Exact authorized-offline identities

- authorized repaired-control commit:
  `86e66cc26801a66742843afaaba714bcd1409cfd`;
- authorized execution-instance SHA-256:
  `1062fd5e9a444c64efc2f240659e8d3d946891365976191b7b44f2c595a5b2b7`;
- authorized schema-6 pre-root envelope SHA-256:
  `6156391ff951b326dd0c303628d223e86ee491e08fdc83ec0af9a3c842618b1e`;
- unchanged 38-attempt index SHA-256:
  `3a6a6047dc8e3ca5c77488a5029bb2165f5b9e71bf32fdc94ec60dcf15ec15e2`;
- authorized 46-file control-tree SHA-256:
  `36d03d421bedaf2904e0421dfd82e3f942c037e5ff9cad268a60746479dd4f93`;
- repaired recapture attestation SHA-256:
  `d84efdaa5dabdd83d3e61523fe98e15a25979cface08081f67cf00e8d08c56da`;
- canonical snapshot SHA-256:
  `df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7`;
- product source commit:
  `1884c0f1c53c661495576bf10ce08d8bf7a90bc3`;
- product archive SHA-256:
  `ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549`;
- qualification source commit:
  `834d05c5c5da0c383c4a229eaeff9dae07a4359b`;
- qualification archive SHA-256:
  `d931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0`;
- qualification-install identity SHA-256:
  `c4bdf3e066527941e5762229d0162b738bea542ec8d47a2cdfda0e66ef7a0ebb`;
- predecessor package inventory SHA-256:
  `7130a4950dd00f04f4c74a55d3a41976a59752f95d269294a5aefa68644a5fad`.

The superseded envelope
`aa07ee829ee01d0bdcdfbc3c0882b2ddd582c9f48c5e8b69253b315522a47e9c`
and every authorization bound to it remain retired and must not be reused.

## Repaired artifact and path closure

The envelope declares 64 inputs, eight release inputs, 55 transition files,
22 installed tools, 28 predecessor package paths, and 28 successor package
paths. The staged executor and pre-root module resolve from the qualification
closure under `control-set/scripts/`; the administrator resolves from the
extracted 54-file product closure. The exact 118-path offline rehearsal has
already reconstructed these closures and executed the archived pre-root entry
point successfully. Target validation must reconstruct the same closures; it
must not patch or reuse the retired staging graph.

## Authorized work only if the exact phrase is supplied

1. Confirm the repository remains clean and synchronized at the exact commit
   above and that every local control identity matches this prompt.
2. Immediately before transfer, stream the exact reviewed read-only snapshot
   tool into privileged Python on `wspr5` twice without installing it or
   creating a target tool file. Require both captures to be 7,083 bytes,
   byte-identical to each other, and byte-identical to the canonical snapshot.
3. Require the exact inactive predecessor state: the Phase 5.53 staging path,
   qualification root, pre-root journal, and attempt namespace absent; runtime
   and all six declared services inactive; exact predecessor package paths and
   terminal predecessor ledger intact; Si5351 disconnected and unused; SDR
   unused; and antenna disconnected. Any mismatch exhausts this authorization
   before transfer.
4. Build a metadata-free transport containing exactly the 64 envelope-declared
   inputs plus the separately sealed envelope. Validate its complete member
   allowlist, hashes, types, modes, ownership policy, duplicate rejection,
   traversal rejection, links, special files, extended attributes, and
   forbidden paths before and after transfer.
5. Extract only at
   `/home/pi/gate-d-inputs/phase5.53-1884c0f1c53c`. Validate every staged path
   and artifact identity, then run read-only validation using the exact staged
   qualification executor and its sealed import closure.
6. Invoke exactly once the authenticated operation
   `phase5.53-pre-root-transition`. It may install only the 28 typed successor
   package paths, copy only the 55 sealed transition files to
   `/home/pi/gate-d-qualification/phase5.53-1884c0f1c53c`, archive only the
   declared terminal Phase 5.52 administrator ledger, and write only the
   declared pre-root journal at
   `/var/lib/rp1-gpclk-dkms/gate-d/pre-root-phase5.53.json` plus exact
   operation-owned transient state.
7. Independently verify the terminal journal and qualification-root marker,
   all transition files and installed tools, the authorized schema-6 execution
   instance, unchanged attempt index, inactive runtime and services, removed
   transport residue, and absent attempt namespace through the installed
   permanent executor and its sealed import graph.
8. Record durable evidence and perform a separate adversarial assessment. Stop
   before lifecycle attempt 1 even when every check passes. Commit and push
   only attributable repository evidence after validation.

On any discrepancy, fail closed and use only exact journal-authorized recovery
paths. Do not improvise cleanup, overwrite unrelated state, or retry the
transition under the same authorization.

## Prohibited work and claim ceiling

No lifecycle attempt may begin. The five deferred rows remain deferred and all
output remains disabled. This slice prohibits GPIO output, active pinctrl,
clock enablement, DMA, module or overlay lifecycle activity outside the exact
pre-root contract, Si5351 or SDR operation, antenna connection, transmission,
RF, `/dev/mem`, forced removal, general upgrade, reboot, and unreviewed boot or
service mutation. Success establishes only authenticated pre-root staging; it
does not establish installation, lifecycle, hardware, timing, coexistence, or
RF qualification.

## Exact authorization phrase

> I explicitly authorize the exact repaired Phase 5.53 target-staging and
> authenticated pre-root slice bound to commit
> 86e66cc26801a66742843afaaba714bcd1409cfd and envelope
> 6156391ff951b326dd0c303628d223e86ee491e08fdc83ec0af9a3c842618b1e,
> including final read-only recapture, validated metadata-free transfer, and
> exactly one pre-root transition. Stop before lifecycle attempt 1; I do not
> authorize any Gate D attempt, GPIO/clock/DMA activity, transmission, or RF.

This decision prompt is non-authorizing. Do not contact the target, transfer
files, create target paths, invoke the administrator or pre-root executor, or
begin an attempt until the operator supplies that exact phrase.
