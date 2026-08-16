<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.20 closed-root-schema adversarial assessment

Status: offline adversarial review passed; candidate frozen

The shared root schema uses an exact five-field object with
`additionalProperties: false`. Bootstrap 2, target plan 4, attempt index 2,
and execution instance 3 require it conditionally; historical versions reject
it. Real Draft 2020-12 validation tests cover positive documents and missing,
extra, renamed, relative, traversal, malformed hash, negative UID, wrong mode,
and wrong-version mutations. All referenced schemas are installed together.

## Findings closed

1. The initial inventory contained no published target-plan or attempt-index
   schemas. Both are now packaged and installed with the shared root schema.
2. Relative references initially resolved against the public `$id` during the
   offline test. Tests now supply the exact local retrieval URI while retaining
   the published identifiers, proving the packaged reference set without
   network access.
3. The first target-plan conditional treated schema 3 like schemas 1 and 2.
   Schema 3 now requires its bootstrap binding while rejecting only the root;
   schemas 1 and 2 reject both newer fields.
4. The shared path schema initially allowed broad `/usr`, `/var`, and `/home`
   roots even though the runtime validator rejected them. Schema and runtime
   constraints now agree, and adversarial tests cover that boundary.

The separate post-implementation audit found no remaining open-root or
version-conditional acceptance path. Two deterministic builds from source
commit `a16a2bb5d3cda2c4442ef82e8ddd21cedbabd9ff` were byte-identical; the frozen
archive SHA-256 is
`62d975ed8972256ecbd274a140bf1bc8639f476516410c82385c528fddff1db3`.
