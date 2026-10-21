<!-- SPDX-License-Identifier: MIT -->

# Route qualification evidence

The published software is `v1.0.0`, product/module/controller `1.0.0`, Debian
`1.0.0-1`. Its original tag, source and seven assets remain immutable. The
original compatibility manifest has `defaultState: Unavailable` and no entries;
qualification evidence does not rewrite it.

WsprryPi distributes a verified local evidence bundle with its application.
There is no separate GitHub qualification release to discover, download or
refresh. The bundle records accepted evidence independently of provider
admission, operational readiness and application band/mode policy.

## Source and scope

The maintained [software binding](../../release/software-1.0.0.json) preserves
all original hashes. The [evidence input](../../release/qualification-1.0.0-r1.json)
binds independent GPIO4/GPIO20 records, module/build observations, both UAPIs,
overlays, retained evidence integrity references and reuse limits. Raw captures
remain in the owning external evidence store.

Each route has its own seven finite conducted TONE cases at 14,097,100 Hz,
2 mA and nominal 200 MHz `pll_sys`. These cases do not establish every band,
mode, board, kernel, frequency, power or spectral claim. The maintained
[application band table](https://wsprry-pi.readthedocs.io/en/devel/About_Wsprry_Pi/index.html#band-qualification)
remains WsprryPi's application qualification authority, maintained and explicitly
accepted by Lee Bussy, who holds its evidence provenance. The table is not
inferred from the finite TONE cases or converted into a provider allowlist.

## Reconstruct the application bundle

The exact metadata source is `bb6815446beb9b96853ad5a353b0d355d4975710`.
Resolve that source by its full commit. The metadata's `metadataTag` field is
a stable evidence identifier; WsprryPi consumes the application bundle locally.

Use a clean checkout of that exact source with Git history and the original
software tag available. Do not substitute maintenance HEAD. Keep temporary
outputs outside checkouts. Reconstruction requires Python `jsonschema`, `dtc`
and `fdtput`, and independently verified original software assets:

```sh
python3 -B scripts/qualification_metadata.py \
  --source-commit bb6815446beb9b96853ad5a353b0d355d4975710 \
  --original-directory /absolute/verified-v1.0.0-assets \
  --directory /absolute/local-evidence
python3 -B scripts/qualification_metadata.py \
  --source-commit bb6815446beb9b96853ad5a353b0d355d4975710 \
  --original-directory /absolute/verified-v1.0.0-assets \
  --directory /absolute/local-evidence --validate
```

The bundle is exactly `rp1-qualification.json`, `rp1-qualification.schema.json`,
`qualification_status.py` and `SHA256SUMS`. Its source/tree/input identity,
original software bindings and every file digest must match WsprryPi's
`release_tools/rp1-qualification-lock.json` before consumption. WsprryPi keeps
these four consumed files in `release_tools/rp1-qualification/` and installs
all of them with its helper and lock. No metadata release publication is part
of this workflow.

The generator checks executable/build equivalence, independent route evidence,
overlay reconstruction, UAPIs and schema. Changed inputs require an explicit
applicability decision and intentional consumer-reference update. Version
equality alone is insufficient. Neither metadata maintenance nor reconstruction
changes the frozen software release or grants target/RF authority.

## Diagnostics

Use WsprryPi's maintained `rp1_qualification.py status` for installed scoped
status. It reads its installed sibling bundle and checks exact package/source,
UAPIs, route, runtime inventory and loaded module build notes against a bounded
provider inspection. Inspection on a target requires separate authorization.
The frozen `v1.0.0` diagnostic collector's aggregate summary cannot establish
current qualification or output inhibition.

The independently usable interpreter accepts explicit local inputs:

```sh
python3 qualification_status.py --metadata rp1-qualification.json \
  --lock /absolute/accepted-evidence-lock.json \
  --provider-report /absolute/runtime-provider-inspection.json \
  --ownership /absolute/installation-ownership.json --route gpio4
```

Structural `Compatible-unqualified`, external scoped evidence, readiness,
output inhibition, ownership and cleanup remain separate facts. Missing or
corrupt installed data is an installation-integrity problem, not hardware
unavailability or a new band/mode restriction.
