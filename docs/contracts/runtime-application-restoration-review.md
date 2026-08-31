<!-- SPDX-License-Identifier: MIT -->

# Application restoration adversarial assessment, 2026-08-31

Scope: schema-3 route switching, application inhibition/ownership, configuration
handoff, idle restart, durable recovery and operator reporting. The kernel module,
controller ioctl implementation, UAPI and RF qualification are unchanged.

## Findings repaired and reassessed

| Finding | Resolution and evidence |
| --- | --- |
| Existing mask mechanism collides with the application's installed service unit | Exclusive, owned condition drop-in; real temporary-file tests preserve foreign units and drop-ins |
| Requesting application dies before it can finish configuration or restart itself | Independently systemd-owned manager worker performs completion; durable query results survive requester loss |
| Starting while holding the controller lock deadlocks startup reconciliation | Separate workflow lock; release controller lock before start; integration test makes independent startup requests during restoration |
| A short readiness poll can race nonblocking startup lock admission | Bounded admission wait only; no retry of kernel/module effects |
| Captured application intent can survive a crash before the first overlay journal exists | Explicit neutral recovery handles capture-only transactions; every durable journal boundary has a tested recovery path |
| A second switch can inherit the previous stopped application's startup override | Journal both ownership tokens; replace/remove only an attributable override, including during recovery |
| Deployment inhibition can precede the first application journal | Recognize the exact project-owned inhibit drop-in without assuming a previously running application |
| Always/Follow boot policies can resume transmission after service restoration | Startup-only idle override; WsprryPi tests all three policies while retaining the saved preference |
| A process without an available UI could acknowledge restoration | WsprryPi requires successful startup quiescence, network policy reconciliation and a bound HTTP listener when configured |
| A stale acknowledgement or exited service could be reported as restored | Check token, route, boot, binding, current PID, active service and idle controller; repeat process check before completion |
| Stored completion can conceal current route/configuration mismatch | Application UI requires matching current controller, boot, binding and configured pin; failed restoration is distinct from route failure |
| Output reconciliation can race the application-phase check | Check both under the same controller lock |
| Bootstrap installer may run outside its selected checkout | Companion installation uses LOCAL_REPO_DIR; offline stubbed installer test verifies source selection and dry-run behavior |

The final source reassessment found no remaining actionable findings within the
implemented canonical-service, offline scope. This is a source/testing conclusion,
not a claim of target service or hardware qualification.

## Validation

- DKMS `make check`: passed, including controller entrypoint mocks, lifecycle,
  module/overlay contracts, compatibility, deployment recovery, licensing,
  documentation links and whitespace checks.
- `python3 tests/check_runtime_restoration.py`: 15 tests passed, including a
  recovery run for every durable journal-write boundary in a successful switch.
- Existing low-level manager and output suites: 16 and 5 tests passed.
- WsprryPi Debian release build and route-service/runtime-wiring tests: passed.
- WsprryPi `semantics-test` in a fresh, network-disabled Debian container:
  passed, including boot-policy, cleanup, UI-source and GPIO-policy regressions.
- WsprryPi companion tests: 7 passed; route UI behavior tests and installer shell
  syntax checks passed.
- Impeccable review used the incumbent interface. Local headless renders at
  1280px and 390px widths showed no horizontal overflow. Browser checks covered
  failed preflight, disconnect handling and prevention of automatic switch retry.

An initial broad semantics run encountered pre-existing mixed Mac/Linux build
products. A fresh container copy, retaining required Git metadata and excluding
build products, passed. A C++ JSON/string comparison caught during the final
build was corrected and the affected build/tests rerun successfully.

No target connection, installation, service change, GPIO/clock/DMA operation,
reboot or RF test was performed. The next validation is a separately authorized
coherent deployment and clock-disabled service/route restoration run, ending on
GPIO20. Supported command layouts and legacy-mask migration are documented in
[the implementation contract](runtime-application-restoration-v1.md).
