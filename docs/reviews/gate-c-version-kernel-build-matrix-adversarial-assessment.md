<!-- SPDX-License-Identifier: MIT -->

# Gate C version/kernel build-matrix adversarial assessment

## Scope

This review attempts to falsify the three authorized representative builds,
their version/kernel separation, evidence integrity, cleanup, readiness effect,
and claim ceiling. It does not assess DKMS, installed rollback, booting the
prior kernel, signing, loading, binding, overlays, services, GPIO, clock, DMA,
transmission, SDR, or RF behavior.

## Findings reinjected

1. Both frozen archive hashes matched before extraction, and every retrieved
   evidence file passed its per-directory checksum manifest. Source commit,
   archive, UAPI, config, `Module.symvers`, module hash, version, and vermagic
   are recorded independently for each build.
2. The files named `build-end-utc.txt` were written during later evidence
   collection rather than immediately at compiler exit. They must not be used
   as build-duration measurements. The evidence summary now states this
   limitation; exit status and complete build logs remain authoritative.
3. The predecessor and successor share a kernel-computed `srcversion`, but
   their declared module versions, frozen source/archive identities, and module
   SHA-256 values remain distinct. The transition pair is not collapsed.
4. Building against installed `6.12.75` headers does not prove that kernel was
   booted, that either module loads there, or that downgrade/rollback succeeds.
   It supplies only the exact build prerequisite for the future lifecycle row.
5. The build results initially closed blockers phrased as positive release
   manifest entries. The durable claim is instead the separately hashed Gate C
   execution build manifest, at `Compatible-unqualified` and
   `liveEligible: false`; no published release manifest was rewritten.
6. All three disposable build directories are absent, retained evidence is
   read-only, and post-build checks show the module and driver absent. No DKMS,
   installation, signing, load, bind, overlay, boot, GPIO, clock, DMA, or RF
   action is evidenced.
7. With these prerequisites, `inputsReady` may become true, but
   `executionReady` must remain false until a fresh explicit target-execution
   release is recorded. The five deferred environmental rows remain unpassed
   and still block complete environmental coverage and publication.
8. The readiness validator initially continued to report
   `blocked-input-required` after every input blocker was closed. It now reports
   the distinct remaining condition: fresh target-execution authorization is
   required.

## Final disposition

No unresolved finding remains within the authorized three-build slice. All ten
required-executable rows have exact inputs. The next gate is fresh target
execution authorization, not an inference from build success.
