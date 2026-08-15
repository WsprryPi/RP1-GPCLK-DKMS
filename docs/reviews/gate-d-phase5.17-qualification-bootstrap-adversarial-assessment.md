<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.17 qualification-bootstrap adversarial assessment

Status: offline software review passed; candidate frozen before target evidence

## Review target

Phase 5.17 introduces a separate qualification-install entry condition so an
exact unpublished candidate can install its permanent output-disabled Gate D
executor. Normal release installation policy is unchanged.

## Assertions

1. Normal installation rejects `publishable: false` candidates.
2. Qualification mode rejects publishable or tagged artifacts.
3. Both the explicit qualification flag and a real identity file are required.
4. The identity has a closed schema and binds release, source commit, archive
   digest, fixed purpose, and output-disabled invariants.
5. Missing, changed, swapped, symlinked, stale, or path-substituted identity
   inputs fail before transaction creation.
6. Archive digest and release checksums remain independently enforced.
7. Qualification mode adds no module load, overlay activation, service, boot,
   GPIO, clock, DMA, SDR, transmission, or RF operation.

Target evidence and execution are outside this offline assessment.

## Findings closed

- CLI path resolution initially erased evidence that an identity path was a
  symlink. The CLI now makes relative paths absolute without resolving them;
  the validator sees and rejects the symlink itself.
- Exact equality alone initially permitted malformed commit or digest strings.
  The identity now additionally requires lowercase 40-hex commit and 64-hex
  archive identities.
- Historical phase-specific qualification bundles could have entered a later
  source archive. The release builder now excludes phase-qualified attempt
  directories and representative/control-set sidecars by closed filename
  patterns.
- Release-gate state inherited stale Phase 5.16 evidence. Phase 5.17 begins
  blocked at candidate freeze and does not reuse prior target evidence.

The complete offline suite passes with normal unpublished-install rejection,
successful synthetic qualification bootstrap, coupled-flag enforcement,
identity mutations, symlink rejection, archive verification, recovery, and
the pre-existing output-disabled safety tests.

The successor is frozen at source commit
`10ec47d83fe49f40c9846df72b8c9e691f6d07a5`; two deterministic builds produced
archive SHA-256
`c13d3c9a38875abb43a9431e498c7a45da4ef964d61ca688ff3dc9f95817050b`.
No Raspberry Pi was contacted. Representative compilation, target-built helper
sealing, renewed route and attempt documents, and fresh execution authorization
remain separate gates.
