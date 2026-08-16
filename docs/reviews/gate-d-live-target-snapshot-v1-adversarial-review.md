<!-- SPDX-License-Identifier: MIT -->

# Gate D live-target snapshot v1 adversarial review

Status: offline process repair accepted; no successor freeze, build, control
set, authorization, staging, or target execution performed.

The capture tool derives package membership from the current administrator
ledger's committed replacement records and measures every resulting path from
the filesystem. It does not consume a historical envelope or generated package
inventory. The same canonical snapshot binds the ledger itself, terminal
recovery, kernel and signing identities, inactive runtime and services, and
explicit physical safety declarations.

The comparison validator is a separate implementation and does not import the
capture tool or a control-set generator. It independently checks canonical
package ordering and digest, complete ledger identity and semantics, terminal
recovery, kernel identity, runtime, services, physical declarations, and exact
equality between snapshot-derived control fields.

Adversarial review found and corrected two initial defects: a capture timestamp
would have prevented byte-identical recapture, and a non-inactive service could
have been mislabeled absent. Canonical bytes now exclude nondeterministic time,
and every reviewed service must report exactly inactive.

Regression tests prove that current package paths combined with a stale ledger
reject, a changed live ledger rejects old controls, an active service rejects
capture, unsafe signing state rejects, and malformed package identity or digest
rejects validation. Focused checks and the complete offline suite pass.

Before any future freeze, the remaining gate is a separately authorized
read-only capture on `wspr5`, preservation of its exact canonical bytes, and an
independent validation run. A second byte-identical capture must pass
immediately before any later authorization request.
