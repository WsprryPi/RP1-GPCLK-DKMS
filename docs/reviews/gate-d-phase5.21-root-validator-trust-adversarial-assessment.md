<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.21 root-validator trust adversarial assessment

Status: offline circular-trust review passed; candidate frozen

The review covers the circular-trust boundary, installed versus staged
identity selection, root marker and target-plan binding, allowlisted installed
path, source/installed equality, verified-byte module loading, bootstrap
retention, normal preflight, and execution outside a checkout. Adversarial
tests cover missing, extra, wrong-path, wrong-source, wrong-installed-hash,
symlinked, and post-bootstrap-substituted validator bytes.

## Findings closed

1. The first trust-bootstrap draft checked only final paths. It now rejects
   symlinked intermediate components beneath the qualification root.
2. The target plan and root marker were initially hashed and then reopened.
   Each is now read once, hashed, parsed, and retained as the verified bytes.
3. Root-marker semantics were initially deferred to the authenticated module.
   The standard-library preamble now enforces the exact marker identity before
   selecting or loading validator code.
4. The staged and installed trust paths are distinct: staged bootstrap must be
   the exact root-owned executor source and loads the exact root-owned
   validator source; installed dispatch requires the allowlisted installed
   executor and validator identities.
5. The bootstrap contract now requires exactly one retained installed
   root-validator identity, and schema-4 target-plan validation requires that
   hash to equal the tooling identity.

The execution instance supplied by the operator remains the outer trust
anchor. After the minimal preamble authenticates the root validator, the full
instance, target-plan, attempt-index, authorization, and candidate checks run
before mutation. Verified validator bytes are compiled directly into the
module object, eliminating a verify-then-import reopen window. Normal attempt
preflight rechecks the installed file identity, detecting later substitution.

## Freeze evidence

The reviewed implementation is source commit
`d0046092dfa9ffa0c58171ddcb52b7819cc50fc6`. Two clean deterministic builds
produced byte-identical
`rp1-gpclk-dkms-0.0.0-phase5.21.tar.gz` archives with SHA-256
`fc5828d91446843d8ea78a09691c973d74082bea7655b6c0547a06d35fba1624`.
The complete offline suite passed twice after that implementation commit. This
freezes an offline candidate only; it supplies no representative-system,
installation, lifecycle, GPIO, clock, DMA, transmission, SDR, or RF evidence.
