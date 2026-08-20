<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 target-staging and pre-root authorization decision prompt

> **Superseded:** the envelope bound by this prompt failed closed because its
> qualification executor paths still targeted the product archive. The exact
> authorization phrase below is retired and must not be reused. Repaired
> controls require a new decision prompt and new explicit authorization.

The operator may authorize only the Phase 5.53 pre-attempt staging and
authenticated pre-root transition bound by these exact identities:

- authorized-offline-controls commit:
  `2d1a5c3e5ca2388679423aa4f2f0f07a56c2d830`;
- original control-set commit:
  `2838380a639d7af71ddc53be20829efd56cedc1d`;
- product source: `1884c0f1c53c661495576bf10ce08d8bf7a90bc3`;
- product archive SHA-256:
  `ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549`;
- qualification source: `834d05c5c5da0c383c4a229eaeff9dae07a4359b`;
- qualification archive SHA-256:
  `d931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0`;
- canonical and preauthorization-recapture snapshot SHA-256:
  `df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7`;
- preauthorization-recapture attestation SHA-256:
  `b53c07ac634936339469a6f1345717f20ec7d1e40855656df83ffd9c1780a6d7`;
- authorized execution-instance SHA-256:
  `6b9125621ed7047feaf5649798edaca73c72c9685d08848bbe95f7b9ed857027`;
- authorized schema-6 pre-root envelope SHA-256:
  `aa07ee829ee01d0bdcdfbc3c0882b2ddd582c9f48c5e8b69253b315522a47e9c`;
- unchanged 38-attempt index SHA-256:
  `3a6a6047dc8e3ca5c77488a5029bb2165f5b9e71bf32fdc94ec60dcf15ec15e2`;
- qualification-install identity SHA-256:
  `c4bdf3e066527941e5762229d0162b738bea542ec8d47a2cdfda0e66ef7a0ebb`;
- predecessor inventory SHA-256:
  `17220ae534936e55fc1710edcd8cebff88add93adb82bd607e020714569a175d`;
- successor release-input inventory SHA-256:
  `b3ae7d71aa1eb8881450b068f9c3525ecf33925ab797419c735b9f4f5aca18cb`.

Authorization is limited to a pre-attempt slice. It permits one final pair of
read-only canonical captures; deterministic construction and transfer of a
metadata-free archive containing exactly the 64 envelope-declared inputs and
the separately sealed envelope; extraction only at
`/home/pi/gate-d-inputs/phase5.53-1884c0f1c53c`; complete target-side path,
type, mode, ownership, regular-file, hash, archive-member, link, special-file,
extended-attribute, and forbidden-path validation; read-only validation with
the exact archived pre-root tool; and exactly one authenticated invocation of
operation `phase5.53-pre-root-transition`.

The eight release inputs are the product archive, qualification archive,
GPIO4 DTBO, GPIO20 DTBO, compatibility manifest, provenance, release metadata,
and checksums. The pre-root transition may install only the 28 typed successor
package paths and copy only the 55 sealed transition files into qualification
root `/home/pi/gate-d-qualification/phase5.53-1884c0f1c53c`. It may archive
only the exact terminal Phase 5.52 administrator ledger declared by the
envelope. The pre-root journal is limited to
`/var/lib/rp1-gpclk-dkms/gate-d/pre-root-phase5.53.json`.

Immediately before transfer, capture `wspr5` twice using the exact reviewed
read-only tool streamed directly into privileged Python, creating no target
tool file. Both captures must be byte-identical and equal the committed
7,083-byte snapshot. Require the staging path, qualification root, pre-root
journal, and attempt namespace absent; runtime and all six services inactive;
the exact 28-path predecessor inventory and terminal ledger intact; Si5351
disconnected and unused; SDR unused; and antenna disconnected. Any mismatch
invalidates authorization before transfer.

After transfer and before transition, require exact equality with the complete
allowlist and zero extra, missing, duplicate, metadata, link, special, unsafe,
or extended-attribute content. After the transition, independently verify the
terminal pre-root journal and marker, all 55 transition files, all 22 installed
tools, authorized schema-6 execution instance, unchanged attempt index,
inactive runtime and services, removed transient transport, and absent attempt
namespace. Validate through the exact installed permanent executor and its
sealed import graph.

Stop before lifecycle attempt 1. This authorization does not permit any of the
38 attempts to start. The five deferred rows remain deferred. Output remains
disabled. GPIO output, active pinctrl, clock enablement, DMA, Si5351 or SDR
operation, antenna connection, transmission, RF, `/dev/mem`, forced removal,
general upgrade, and unreviewed boot mutation are prohibited. Stop and recover
only through exact journal-authorized paths on any discrepancy.

The exact authorization phrase is:

> I explicitly authorize the exact Phase 5.53 target-staging and authenticated
> pre-root slice bound to commit
> 2d1a5c3e5ca2388679423aa4f2f0f07a56c2d830 and envelope
> aa07ee829ee01d0bdcdfbc3c0882b2ddd582c9f48c5e8b69253b315522a47e9c,
> including final read-only recapture, validated metadata-free transfer, and
> exactly one pre-root transition. Stop before lifecycle attempt 1; I do not
> authorize any Gate D attempt, GPIO/clock/DMA activity, transmission, or RF.

This prompt does not itself authorize staging or the pre-root transition. Do
not contact the target, transfer files, create the staging path or qualification
root, invoke the administrator, or begin an attempt until the operator supplies
that exact authorization.
