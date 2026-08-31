<!-- SPDX-License-Identifier: MIT -->

# Runtime output integration review

Scope: connect the existing runtime route to WsprryPi's existing ABI-v4
operation lease, then repair failures exposed by the authorized target test.
Kernel DMA execution and runtime recovery changed. UAPI, global-output setting,
lease mechanism, mode policy, and duration limits did not change.

Adversarial findings resolved:

- The initial proposal added redundant permits and an arbitrary 30-second limit.
  Those edits were removed. Existing application authorization and kernel leases
  remain authoritative in the closed administrative system.
- Documentation claimed the instrumented consumer could never output. The
  existing ABI-v4 acquire disproves that claim; the contract now distinguishes
  the load parameter from per-operation authorization.
- Legacy boot ownership cannot reconcile a runtime overlay. Explicit schema-3
  reconciliation now validates current controller/journal/module observations.
- Startup must not clear transmission inhibition merely because a route exists.
  Idle reconciliation keeps inhibition. Development reconciliation only supplies
  route readiness to the already existing operation authorization path.
- Synchronous service start while holding the manager lock can deadlock startup
  reconciliation. Explicit resume only unmasks; service start happens afterward.

Validation: complete module offline suite passed; runtime manager/deployment
16 tests and new output reconciliation 5 tests passed; companion C++ route-service
and runtime-wiring tests passed, including successful idle/development queries,
route mismatch, and rejection of a manager claiming output authorization.
The 392-byte passive snapshot decoder was exercised on wspr5 while output was
disabled and reported GPIO20, no owner/lease, and safe GPIO/clock/DMA state.

Target testing found and closed these additional issues:

- The stock DMA provider split a large entry into non-word-aligned lengths.
  Aligned scatterlist entries conserve the original sample count and addresses.
- Clearing tick requests on an intermediate DMA block stalled the linked
  descriptor. Requests now continue until descriptor completion.
- Cancellation hid a DMA completion timeout. Deadline failures are now retained
  with provider status/residue diagnostics.
- A read-only DREQ pulse was misidentified as an ownership conflict. Capture and
  restoration compare writable configuration without that pulse.
- Startup unwind could stop ticks that had not been acquired, or stop the
  restored firmware baseline on a second cleanup pass. Tick ownership is now
  established after validation and cleanup acts only while that ownership remains.
- A previous boot's journal prevented recovery of an empty new controller.
  Explicit recovery preserves the old journal and records the neutral new boot;
  it cannot adopt a nonempty controller or bypass artifact binding checks.
- The companion application terminated on a worker exception, omitted backend
  records, dropped TONE terminal reasons, and could report a cleanup failure as
  success. Its worker and response paths now preserve those failures. Final
  review also removed stale operation records from asynchronous start replies.

The full module offline suite, 18 controller tests, companion route-service,
runtime-wiring, backend, cleanup-lifecycle and response regression tests passed.
Both projects built on the exact stock target kernel. Repeated GPIO20 20m
10-second operation and cleanup succeeded, followed by supported reboot recovery.
See [target evidence](../evidence/runtime-tone-20260831/README.md). No unresolved
finding remains in this bounded implementation scope. These results do not prove
RF frequency accuracy, electrical silence, GPIO4 behavior, or product qualification.

External follow-up: the Harness WebSocket client rejects ping control frames.
The diagnostic client used for the final test handles ping/pong; the Harness
repository itself was not changed. Its complete WSPR/QRSS campaign remains unrun.
