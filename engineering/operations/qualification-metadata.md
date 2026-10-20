<!-- SPDX-License-Identifier: MIT -->

# Supplemental qualification metadata

Software `v1.0.0`, product/module/controller `1.0.0` and Debian `1.0.0-1`
retain their original tag, source and seven assets. Their original compatibility
manifest has `defaultState: Unavailable` and no entries. Reconstruct and validate
it with the tagged [release procedure](release-candidate.md).

Qualification metadata has a separate identity, `qualification-v1.0.0-r1`.
That revision is already published. Reconstruct it from its exact immutable
metadata tag/source and verify downloaded assets; do not rebuild maintenance
HEAD as replacement r1 assets or attempt to recreate its existing tag/release.
It records accepted evidence; it does not create qualification. It is not a
module release, package update, admission credential or execution permission.
WsprryPi's semantic-version release selector excludes this tag. Publication
must explicitly retain `v1.0.0` as GitHub's latest software release.

The maintained [software binding](../../release/software-1.0.0.json) preserves
all original hashes. The [evidence input](../../release/qualification-1.0.0-r1.json)
binds route-specific records, integrity references, module/build observations,
both canonical UAPIs, packaged and runtime overlay identities, scope, exclusions
and reuse decisions. Raw captures and execution records remain in the owning
external evidence store. Evidence URNs identify those retained records; their
SHA-256 references permit independent integrity checks.

Each route has its own seven finite conducted TONE cases at 14,097,100 Hz,
2 mA, nominal 200 MHz `pll_sys`. These cases do not establish other band/mode,
calibrated-frequency, power or spectral claims. The separate maintained
[application band table](https://wsprry-pi.readthedocs.io/en/devel/About_Wsprry_Pi/index.html#band-qualification)
remains WsprryPi's qualification authority. The table's scope is not inferred
from the TONE cases, nor promoted into a provider-side band/mode allowlist.
Lee Bussy maintains the evidence and its provenance and explicitly accepts
that table as the established application qualification scope. This acceptance
and the exact route/build evidence are complementary authorities.
Board, kernel and compiler observations do not create compatibility gates.

The generator checks unchanged executable, build, UAPI, overlay and lifecycle
inputs between accepted and released provider sources. Candidate and released
package archives retain different hashes even where extracted payloads match.
Changed inputs require a new applicability decision; version equality alone
is insufficient.

## Reconstruct and validate

For existing r1, use a clean checkout of its immutable metadata tag, with Git
history and the original software tag available. `EXACT_METADATA_COMMIT` below
means that tag's exact peeled commit, not maintenance HEAD.
Keep output outside checkouts. The generator requires Python `jsonschema`,
`dtc` and `fdtput`; it reconstructs and verifies both overlay forms.

```sh
python3 -B scripts/qualification_metadata.py \
  --source-commit EXACT_METADATA_COMMIT \
  --original-directory /absolute/verified-v1.0.0-assets \
  --directory /absolute/new-supplement
python3 -B scripts/qualification_metadata.py \
  --source-commit EXACT_METADATA_COMMIT \
  --original-directory /absolute/verified-v1.0.0-assets \
  --directory /absolute/new-supplement --validate
```

The complete publication is exactly four assets: `rp1-qualification.json`,
`rp1-qualification.schema.json`, `qualification_status.py` and `SHA256SUMS`.
Metadata binds its own source commit, tree and input digest separately from
the original software source. Build twice and compare every byte. Complete
offline tests, schema/link/licensing checks, CI and a separate adversarial
assessment before publication.

Initial publication uses an annotated metadata tag and a separate draft release
with `--latest=false`, then uploads the validated four assets and publishes with
`--latest=false` under repository release immutability. Existing r1 is verified,
not recreated. Never replace its assets or upload to, retag or edit `v1.0.0`.
A correction requires a new metadata revision, reviewed generator/input identity
changes and intentional consumer reference update: the current generator fixes
its tag and revision to r1, so a different `--source-commit` alone is not a new
revision mechanism.

Independently download the publication. Revalidate all four bytes, checksums,
metadata tag/source, complete asset inventory and all seven original asset
bindings. Recheck the original tag object/commit and every original asset hash.
WsprryPi separately pins supplemental source, revision and all four asset
digests, verifies the actual publication and runs its real resolver. Its original
release lock remains unchanged. Metadata absence or verification failure must
produce a missing/invalid evidence result without changing operational policy.

## Diagnostics

`qualification_status.py` is the separately identified supplemental interpreter.
The diagnostic collector source at `v1.0.0` is unchanged. Its legacy aggregate
summary cannot establish current qualification: route/compatibility-ID matching
alone is insufficient, and its state-equality rule conflates external evidence
with structural module compatibility.

Use WsprryPi's maintained `rp1_qualification.py status` for installed status,
or use the supplemental interpreter with explicitly supplied metadata, accepted
lock, provider inspection and ownership files. The latter is entirely offline:

```sh
python3 qualification_status.py --metadata rp1-qualification.json \
  --lock /absolute/accepted-supplement-lock.json \
  --provider-report /absolute/runtime-provider-inspection.json \
  --ownership /absolute/installation-ownership.json --route gpio4
```

An installed inspection requires separate target authorization. Exact package,
released source, UAPIs, route, runtime overlays, installed artifacts and loaded
module build notes must agree before attributing published evidence.
Structural `Compatible-unqualified` remains the module's reported state alongside
external scoped qualification. Output inhibition, readiness, ownership and cleanup
remain independent observations. Missing evidence is not hardware unavailability.
