<!-- SPDX-License-Identifier: MIT -->

# Gate C representative-build adversarial assessment

## Scope

This review attempts to falsify the exact source identity, representative
header build, output-disabled boundary, evidence integrity, cleanup, and claim
ceiling recorded for the 2026-08-15 `wspr5` build. It does not assess DKMS,
installation, signing, loading, binding, overlays, runtime behavior, a Gate D
lifecycle row, GPIO, timing, transmission, or RF behavior.

## Assertions and findings

1. The target archive SHA-256 matched the frozen successor before extraction.
   The UAPI copy and resulting module were independently hashed in the evidence
   directory.
2. Kernel, installed header packages, architecture, compiler, config, and
   `Module.symvers` were recorded. The build completed with exit status zero
   and no warning, error, or modpost diagnostic.
3. `modinfo` was absent. Installing it would have exceeded authorization. The
   review accepted `readelf -p .modinfo` because it directly recorded version,
   license, module name, dependencies, and vermagic from the built ELF object;
   the limitation remains explicit.
4. The current config hash differs from the historical Phase 4 config hash.
   Reusing either historical route entry as a positive successor decision
   would be an identity substitution. The new build manifest records only a
   route-neutral `Compatible-unqualified`, non-live result and explicitly says
   that it satisfies neither a route-specific compatibility entry nor a Gate D
   lifecycle row.
5. The evidence-manifest checksum was verified against every retrieved file.
   The retained target directory is read-only, but user ownership and mode
   `0555` are tamper evidence, not cryptographic immutability. Its recorded
   manifest digest remains the integrity boundary.
6. The exact disposable build directory is absent after cleanup. Pre- and
   post-build live-state checks recorded no loaded module or bound driver. No
   evidence indicates DKMS, installation, signing, overlay, service, boot,
   GPIO, clock, DMA, transmitter, SDR, antenna, or RF activity.
7. Naming the result a representative-build manifest could be confused with
   the release compatibility manifest. The document therefore has the unique
   kind `gate-c-representative-build-manifest` and carries explicit negative
   satisfaction fields. It must never be selected by runtime compatibility
   logic.

## Disposition

No unresolved finding remains in the authorized Gate C build slice. The exact
successor build prerequisite is closed at `Compatible-unqualified` with
`liveEligible: false`. Gate D remains blocked: the route-specific release
compatibility decision has not been regenerated and the newer-kernel,
signature-enforcement, missing-header, and genuine-conflict representative
inputs remain unavailable. `--require-ready` must continue to fail.
