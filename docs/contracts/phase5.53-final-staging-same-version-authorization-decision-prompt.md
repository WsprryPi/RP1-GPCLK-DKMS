<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 final staging and same-version authorization decision prompt

## Objective

Permit the operator to authorize one bounded target slice that starts from the
exact inactive product-only installation, performs a final read-only recapture,
transfers and validates the deterministic metadata-free staging closure, and
executes exactly one recoverable same-version product-to-qualification
transition. Stop before lifecycle attempt 1.

This prompt is non-authorizing until the operator supplies the exact phrase at
the end.

## Exact identities

- transport-successor commit:
  `c0bfeb18f12f5eed63f0a00319ca446864056fdd`;
- product archive SHA-256:
  `032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76`;
- qualification archive SHA-256:
  `916a5522e3998ae43f203c217fedce90ad8d4c2d52ae0bd4491407e3cf17211d`;
- canonical snapshot SHA-256:
  `cbaed5a7972bb317a9dc27cabead9419ffde2db474df4de493373b6aa474524f`;
- preauthorization-recapture attestation SHA-256:
  `44b004e1c50f935658ec05cabc9754512b5cd2006b35e7787bc6718f162ef755`;
- final transport-successor evidence SHA-256:
  `c0c26494b6fa73a5aba44a4779924328a897eb08817ae7569611d715e3030a86`;
- deterministic transport SHA-256:
  `f8ea112c2b3ff1fe18c8d48dc54f4ee8a5f41427595a163ddde2907e11c9a73b`;
- transport source-map SHA-256:
  `cdee6830d11baf705a607d9dae2610f56bdd98d79d399781137f6ce52ab5beb2`;
- schema-7 pre-root envelope SHA-256:
  `c32b3f196b48aa0c10da4067173d6025f91c642f7ff3b5c770d5ef5fba5d0bf2`;
- same-version transition plan SHA-256:
  `30f93036c63db3c2ca9a6d14c9905928f940878c12d5d757c0d761ad4eedbb3c`;
- execution-instance SHA-256:
  `ad261cebc42adeaf0f079ca2a94f5bb115cb902d116733a35a7008d29be622af`;
- unchanged 38-attempt index SHA-256:
  `b1fa034d0bc35031c335f607edf4726cc39d89f0ff4bd378687ee5232b5c54a0`;
- qualification-install identity SHA-256:
  `0d5a529f477026ca03965be3cc3c9ad6129f2707996b60603a486e7bea6cfac9`;
- installed product ledger SHA-256:
  `d4fe02f8d66ac298f2076b37be297097f392095904cc3809717713cd01a14f8d`.

## Authorized sequence after the exact phrase

1. Confirm the repository is clean, synchronized, and exactly at the bound
   commit. Revalidate every identity above before target contact.
2. Stream the reviewed read-only capture source directly to privileged Python
   on `wspr5` twice without creating a target tool file. Require both 16,745-byte
   captures to be byte-identical to one another and the canonical snapshot.
   Separately require the staging directory, qualification root, pre-root
   journal, same-version journal, and attempt namespace to be absent. Any
   mismatch exhausts this authorization before transfer.
3. Construct the 151-file USTAR transport twice and require byte identity and
   the exact transport/source-map hashes above. Transfer only those bytes and
   extract only to `/home/pi/gate-d-inputs/phase5.53-4e7a64a0ca35`.
4. Before mutation, validate the complete path set, hashes, file types, modes,
   ownership, archive membership, absence of links and special files, absence
   of PAX metadata and extended attributes, and absence of extra or missing
   paths. Run both staged entrypoints in read-only validation mode.
5. Invoke exactly one staged same-version driver `execute` action with the
   sealed plan and journal
   `/var/lib/rp1-gpclk-dkms/gate-d/same-version-phase5.53-final.json`.
   The driver may perform exactly one ledger-bound inactive product removal,
   verify the absent state, and invoke exactly one authenticated schema-7
   pre-root installation. The pre-root journal is limited to
   `/var/lib/rp1-gpclk-dkms/gate-d/pre-root-phase5.53.json`.
6. If the transition fails or is interrupted, perform only the recovery action
   selected by the sealed same-version journal: recover/remove the exact
   qualification transaction if needed and restore the exact product-only
   state. Do not improvise cleanup or continue after recovery.
7. On success, independently require the terminal same-version and pre-root
   journals, sealed qualification-root marker and files, exact installed tool
   identities, qualified-state probe, inactive module/endpoint/overlay and
   services, output disabled, and absent attempt namespace. Record evidence and
   stop before lifecycle attempt 1.

## Authorization boundary

This slice permits the exact inactive package removal and qualification
installation described above because they are inseparable parts of the sealed
same-version transition. It does not authorize any Gate D lifecycle attempt,
module load/bind/unbind/unload, overlay activation, boot mutation, reboot,
service mutation beyond exact recovery if the sealed transaction requires it,
GPIO or active pinctrl access, clock enablement, DMA, Si5351 or SDR operation,
antenna connection, transmission, RF, `/dev/mem`, forced removal, general
upgrade, or unreviewed cleanup.

The execution instance intentionally remains unauthorized and
`executionReady=false`; this external operator decision authorizes only the
pre-attempt transition described here and does not flow into the 38 attempts.

## Exact authorization phrase

> I explicitly authorize the exact Phase 5.53 final metadata-free staging and
> recoverable same-version product-to-qualification transition on wspr5 bound
> to commit c0bfeb18f12f5eed63f0a00319ca446864056fdd, transport
> f8ea112c2b3ff1fe18c8d48dc54f4ee8a5f41427595a163ddde2907e11c9a73b,
> same-version plan
> 30f93036c63db3c2ca9a6d14c9905928f940878c12d5d757c0d761ad4eedbb3c,
> and pre-root envelope
> c32b3f196b48aa0c10da4067173d6025f91c642f7ff3b5c770d5ef5fba5d0bf2,
> including the final byte-identical read-only recapture, validated transfer,
> exactly one ledger-bound inactive product removal, and exactly one
> authenticated qualification installation with sealed recovery. Stop before
> lifecycle attempt 1. I do not authorize any Gate D attempt, module or overlay
> activity, reboot, GPIO/clock/DMA activity, transmission, or RF.

Until that exact phrase is supplied, do not contact `wspr5`, construct or
transfer target staging bytes, create target paths, invoke the administrator,
same-version driver, or pre-root executor, or begin an attempt.
