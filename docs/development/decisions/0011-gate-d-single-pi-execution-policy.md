<!-- SPDX-License-Identifier: MIT -->

# Decision 0011: Gate D single-Pi execution policy

Status: accepted
Date: 2026-08-15

## Context

The base representative-system matrix deliberately contains fifteen distinct
assertions. The available target inventory has one Raspberry Pi 5 and cannot
truthfully provide a newer unknown stock kernel, signature enforcement with an
enrolled key, a genuinely missing-header installed kernel, or a pre-existing
foreign route conflict. Fabricating those identities would test policy code,
not representative system behavior.

Editing the frozen candidate's packaged base matrix would change candidate
source inputs and invalidate its Gate C build. The concrete execution instance
and its policy are test-control sidecars rather than candidate module bytes.

## Decision

Keep every base-matrix assertion unchanged. Apply the separately hashed
`release/gate-d-matrix-policy-v2.json` to classify each row as either
`required-executable` on the available target or `deferred-environmental`.
Execution readiness considers only required-executable rows. Environmental
coverage and publication still require genuine evidence for all fifteen rows;
a deferred row never passes, disappears, or becomes simulated evidence.

Record the exact current route decision separately in
`release/gate-d-route-compatibility-decision-v1.json`. Gate C proves the module
build, but current firmware, base-device-tree, provider, resource, and conflict
identity were not captured under that authorization. GPIO4 and GPIO20 are
therefore independently `Unavailable`, output-disabled, and unauthorized for
installation or binding until a read-only identity refresh supports a newly
reviewed release-manifest decision.

## Consequences

The policy revision does not mutate the sealed candidate and does not make
Gate D executable yet. It reduces ambiguity: five environmental rows are
deferred, eight required-executable rows remain blocked by exact route or
predecessor inputs, and two negative integrity rows are ready. A future
`inputsReady: true` will mean only that the required-executable subset has
complete inputs. A fresh explicit target-execution release must additionally
set `targetExecutionApproved: true` before `executionReady` or
`--require-ready` can pass. That execution release will cover only the
required-executable subset;
`environmentalCoverageComplete: false` will continue to prohibit claims of
complete matrix coverage, publication readiness, or qualification.

## Read-only identity follow-up

The subsequently authorized read-only `wspr5` discovery recorded the current
firmware, base device tree, stock RP1 clock/DMA/pinctrl providers, route groups,
static conflict state, signing policy, installed kernels, and headers. GPIO4
and GPIO20 now have separate `Compatible-unqualified`, non-live execution
decisions. These decisions are Gate D sidecars, not a rewritten published
release manifest and not target-mutation authority. Immediate fail-closed
preflight remains mandatory.

Seven required-executable rows are now ready. Three predecessor-dependent rows
remain blocked, and the five environmental rows remain deferred.

## Version/kernel build follow-up

The three authorized disposable builds subsequently passed: predecessor
`0.0.0-phase5.2` against current and prior stock headers, and successor
`0.0.0-phase5.13` against prior stock headers. All ten required-executable rows
now have exact inputs and `inputsReady: true`. This is build compatibility, not
an installed rollback result. `targetExecutionApproved` and `executionReady`
remain false pending a fresh explicit execution release.
