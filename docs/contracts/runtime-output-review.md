<!-- SPDX-License-Identifier: MIT -->

# Runtime output integration review

Scope: connect the existing runtime route to WsprryPi's existing ABI-v4
operation lease. No kernel code, UAPI, global-output setting, lease mechanism,
mode policy, or duration limit changes.

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

Remaining target work: coherent manager/application update, idle startup, the
user-authorized 20m 10-second TONE, and verification of output shutdown. Neither
these offline tests nor the passive snapshot prove RF frequency or electrical
silence. Target results must be recorded separately.
