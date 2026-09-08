<!-- SPDX-License-Identifier: MIT -->

# Application update preparation

The provider owns interpretation of controller sessions, generations, activation
ancestry, route journals, deployment recovery and provider service state.
Applications own version selection, their configuration and installation
provenance. An application must not reconstruct provider recovery decisions.

## Public interface

`runtime_provider.py capabilities` advertises
`rp1-gpclk-runtime-update-v1`. `update-plan` is read-only and returns the next
bounded step toward removal of the runtime deployment. `update-execute` accepts
only its reviewed SHA-256. Both accept `--source-commit` and optional paired
`--binding-sha256` / `--artifact-set-sha256` from application installation
provenance. `--deployment-sha256` binds interrupted inverse deployment recovery.

The public envelope contains the contract/version, operation, installation
identity, plan digest, status and postconditions. The plan payload is opaque
to applications: its contents are provider-private evidence. Execution
reconstructs it under application mutation exclusion and rejects drift before
effects. Existing primitives retain their deployment/controller locks and
revalidation. Each effect has its own reviewed step; failed execution is never
automatically retried. A new plan observes the completed or interrupted state.

Successful preparation removes only the exact runtime deployment. The inverse
may restore the application service intent captured before deployment; success
does not promise that the application remains stopped. DKMS package
or source rollback remains the predecessor's lifecycle operation. Preparation
never selects a route or enables transmission. The application may replace its
files only after `prepared` with verified runtime absence. It subsequently
deploys and activates the new provider through the existing public facade.

## Response contract

All successful responses use integer `schemaVersion: 1`, string `contract:
rp1-gpclk-runtime-update-v1`, and the requested `operation`.

- `capabilities` lists `update-plan`, `update-execute`, and
  `installation-status`; it performs no host observations or effects.
- `update-plan` and `update-execute` echo `identity` with `sourceCommit`,
  `bindingSha256`, `artifactSetSha256`, and `deploymentPlanSha256`. Unprovided
  optional digests are JSON null. The source is the installed predecessor's
  40-character lowercase hexadecimal commit, not the candidate's commit.
- `status` is `planned` or `prepared`. `postconditions.runtimeAbsent` is true
  only for `prepared`; `postconditions.transmissionAuthorized` is always false.
- `update-plan` includes `plan` and `planSha256`, the SHA-256 of UTF-8 JSON
  with sorted keys and compact separators. Consumers may verify the hash but
  must not branch on private payload fields. `update-execute` echoes the
  approved digest and returns newly observed status and postconditions.
- `installation-status` returns `status: neutral_ready` and a `receipt` with
  the readiness contract, binding/artifact/source/product/kernel/compatibility
  identities, deployment and activation digests, original activation request
  and controller session, `controllerGeneration: 0`, `state: neutral_ready`,
  `route: null`, and `output: disabled`. Generation zero describes the original
  installation, not a later live controller. The provider validates later
  generations independently.

Consumers must reject missing required fields, unknown contracts/versions,
identity or digest mismatch, contradictory postconditions, and nonzero exit
status. Additional envelope fields are additive. Only the two postcondition
booleans above are defined in version 1. A failure does not authorize a retry or
prove absence. Current CLI failures use the readiness-v1 diagnostic envelope
and a nonzero status; they are never successful update responses.

## Compatibility and recovery

Use the installed provider when it supports this contract. Otherwise an exact,
reviewed provider source may supply the adapter. The adapter explicitly supports
the binding-v3/readiness-v1 predecessor protocol, validates its complete installed
artifact inventory and identities, and uses existing provider-owned lifecycle
primitives. Unknown binding versions, changed artifacts, foreign state, unsafe
output or unproven recovery are refused before mutation.

The selected source must advertise the contract during source resolution,
before package/application mutation, even when no provider is installed. An
older installed provider may be migrated by the selected compatible source;
this does not make older sources or release packages implement the new API.
The same interface applies to uninstall preparation. Application ownership
records remain application-owned. No provider API reads or rewrites WsprryPi's
INI or its installation record directly; existing application companion calls
continue to own idle/service integration policy.

## Acceptance boundary

Offline coverage must include initial neutral, GPIO4/20 selected and idle,
completed removal at later generations, stopped/masked service intent,
interrupted recovery/removal, post-reboot retirement, retries, stale plans,
concurrency, unknown contracts, foreign artifacts, unsafe endpoints and output.
Provider fixtures exercise the real classifier and lifecycle planners; consumer
tests verify the public envelope and delegation without interpreting private
plan contents. Offline tests do not qualify live installation, GPIO or RF.
