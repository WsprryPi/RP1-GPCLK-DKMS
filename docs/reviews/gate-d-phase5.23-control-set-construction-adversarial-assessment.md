<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.23 control-set construction adversarial assessment

Status: blocked before control-set freeze

## Intended slice

The offline slice constructed a candidate Phase 5.23 pre-root envelope,
schema-3 qualification bootstrap, route decision, schema-5 root-bound target
plan, 38-attempt bundle, and schema-4 execution instance. The deterministic
attempt generator produced 38 unique documents, including all 15 interruption
checkpoints and four busy-state attempts. All 38 completed in the stateful
offline fake with restored services, sealed evidence, and live output false.

No Raspberry Pi was contacted or changed.

## Blocking finding: frozen target-plan schema contradicts its validator

The separate JSON Schema validation found that the frozen Phase 5.23 target
plan cannot be valid under both published authorities:

- `schema/gate-d-target-plan-v1.schema.json` defines `attemptEnvelope` as an
  object.
- `scripts/gate_d_target_plan.py` requires `attemptEnvelope` to be an ordered
  list of unique lifecycle operations and rejects an object.
- The permanent attempt generator and executor consume the list form.

The exact constructed plan therefore passes the permanent validator but fails
its published JSON Schema with:

```text
$.attemptEnvelope: [...] is not of type 'object'
```

Changing the plan to an object would make the permanent validator reject it.
Changing either the schema or permanent validator would change bytes already
bound into the frozen Phase 5.23 archive. A sidecar exception, schema bypass,
or claiming that the ordinary suite is sufficient would violate the release
and fail-closed contracts.

## Consequence

No Phase 5.23 control set is frozen or execution-ready. The generated draft
documents were removed after the finding so they cannot be mistaken for
executable inputs. The repository's existing Phase 5.23 candidate and
representative-build evidence remain unchanged.

No commit or push is appropriate for a purported passing control set. This
assessment and its execution prompt remain uncommitted for operator review.

## Required successor

A distinct successor must reconcile the target-plan JSON Schema and permanent
validator, add a regression that validates the exact real plan with the
published schema, repeat the full offline adversarial review, freeze and build
the new candidate, and only then construct a new pre-root and root-bound Gate D
control set. Historical Phase 5.23 identities must remain immutable and be
marked blocked before control-set freeze rather than rewritten.

## Activity boundary

No installation, package, DKMS, signing, module, overlay, service, boot,
reboot, GPIO, clock, DMA, Si5351, SDR, antenna, transmission, or RF activity
occurred. No tag, publication, pull request, or consuming-repository change
occurred.
