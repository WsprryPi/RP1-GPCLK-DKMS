<!-- SPDX-License-Identifier: MIT -->

# Runtime-route v2 offline implementation review

Date: 2026-08-31. Baseline: `818e932`. Scope:
[offline v2 engine and blocked public boundary](runtime-route-v2.md).

## Outcome

The offline engine implements guarded switch planning, dual-route identity
validation, persistent transaction records, same-boot adoption, explicit
resume/rollback and replay rejection. The public entry point cannot connect
to that engine or perform target effects. The requested operational feature
is **not complete**: no real adapter, persistent target admission mechanism,
runtime-overlay ownership mechanism, post-unload attestation, or deployment
integration has been implemented. Those limitations are exposed as blockers,
not represented by an override, success response, or qualification claim.

No module/UAPI/overlay bytes changed. No target inspection, installation,
service administration, GPIO, DMA, transmission, reboot, or RF work occurred.
New independent Python, schemas, and documentation use MIT; original licenses
are unchanged. All work remains separate from package/release qualification.

## Adversarial findings and repairs

| Finding | Repair and evidence |
| --- | --- |
| Safe defaults could let an adapter omit observations. | All safety fields are required and strictly boolean; false/unknown/incorrect primitive fixtures reject execution. |
| A valid hash chain alone did not establish a legal transaction sequence. | Reload validates the initial plan and every subsequent intent, completion and recovery transition; rehashed semantic corruption is rejected. |
| Recovery attribution and request replay needed cross-operation checks. | Switch/recovery IDs share a conflict registry; exact current completed replays are idempotent, stale completions fail, and changed recovery strategy needs a new ID. |
| Adoption syntax alone could renew stale route ownership. | Initial adoption binds boot, identity, route and overlay owner; missing/stale adoption is rejected before effects and during journal replay. |
| A replaced journal could receive writes through an obsolete locked inode. | Each append checks the linked inode, owner, mode and link count; replacement preserves both files and blocks writing. |
| Partial journal writes and size exhaustion required explicit failure behavior. | Records and ledger are bounded; partial data is preserved and blocks reuse. Failure fixtures verify no initial hardware effects. |
| Schema end anchors could accept trailing newlines rejected by the parser. | Patterns require the absolute end of the string; real JSON Schema negative tests cover newline-bearing identifiers and hashes. |
| Restoring services could be mistaken for permission to resume output. | Admission remains closed through restoration and completion; the engine has no admission-release operation. |

After repairs, the second assessment checked effect ordering, artifact
separation, route-neutral and same-route handling, rollback to route-neutral
state, replay after later transactions, process death around every forward
effect and journal write, malformed journals, foreign-state races, ownership
reopening, boot changes, autoload/readback mismatch, and failed rollback.
No additional actionable defect was found in this offline scope. This is a
separate assessment pass by the implementing agent, not an independent-agent
or kernel/hardware audit.

## Validation

- Full `make check`: PASS, using an isolated temporary Python environment with
  `jsonschema==4.23.0` on PATH. The suite reports 34 registered Python checks,
  nine host C tests, and one separately parameterized utility. Target-only
  clients are classified rather than run.
- New `tests/check_runtime_route.py`: 20 test methods PASS, including subcases
  for both directions, same-route and route-neutral start, all seven effect
  boundaries before/after effect, all 15 forward journal-write boundaries
  before/after write, and rollback from every forward effect boundary.
- Both new JSON schemas: Draft 2020-12 validation and positive/negative fixture
  validation PASS with the real validator. Ordinary test runs without that
  optional dependency explicitly skip full schema validation after structural
  checks; this recorded run did not skip it.
- Existing package/development route-manager tests, schema checks, UAPI freeze,
  source/lifecycle checks, deterministic overlay compilation, SPDX,
  documentation links, ShellCheck, host C tests and whitespace: PASS.
- Kernel header builds: not run; no kernel or UAPI source changed. No fixture
  result establishes target module/overlay lifetime safety.

The temporary validator dependency was installed outside the repository;
tests themselves were offline. No project dependency or target configuration
was changed to obtain validation.

## Next work and gate

Implement and review the three missing target mechanisms in the v2 contract
before supplying a Linux adapter or deployment path. Inspect exact target
kernel/tool and provenance information read-only to choose supported interfaces.
A real implementation may require a coordinated additive kernel/application
administration contract; do not invent guarantees in the adapter to satisfy
the offline model. Target mutation remains blocked until that work and its
review are complete and exact administrative operations are separately
authorized. Firmware-route migration still requires an explicit initial reboot.
