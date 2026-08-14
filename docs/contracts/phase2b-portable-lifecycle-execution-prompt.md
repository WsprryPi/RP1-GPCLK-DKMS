<!-- SPDX-License-Identifier: MIT -->

# Phase 2B portable lifecycle execution prompt

## Outcome and boundary

Implement and adversarially review an offline, route-neutral portable core for
exclusive ownership, opaque leases, lease-scoped generations, complete V1
validation, finite work, legal transitions, STOP, RELEASE, owner close, stable
terminal reasons, stale-event rejection, and cleanup-fault latching.

Add deterministic host tests and named fault injection. Prove that every
accepted generation publishes exactly one immutable terminal result and that
stale commands or callbacks cannot mutate a current or terminal generation.

Do not access a Raspberry Pi; register a driver, endpoint, file operation, or
ioctl; install or load a module; use DKMS or overlays; acquire clock, DMA,
pinctrl, device-tree, MMIO, or GPIO resources; change a system; transmit; or
produce RF. The module skeleton remains inert.

## Required assertions

- Acquisition is atomic, single-owner, route allowlisted, and capability
  bounded. Lease and generation zero, wrap, reuse, and cross-owner use fail
  closed without partial mutation.
- Both V1 submissions validate exact header, flags, reserved fields, modes,
  counts, divider/dither relationships, drive values, event flags, symbols,
  durations, and checked sums before allocating a generation. Accepted plans
  are copied into fixed-capacity core-owned storage and logically released
  exactly once on terminal cleanup.
- Work has a deterministic finite unit count. STOP prevents successors and
  permits at most one modeled residual unit. It makes no DMA claim.
- State/reason transitions are centralized. Nonterminal reasons are `NONE`;
  terminal state and reason are committed once and never overwritten.
  A host-only direct probe must prove the central publication guard itself,
  independent of duplicate guards at public operation entry points.
- RELEASE refuses unsafe active work and cannot clear a cleanup latch. Active
  owner close uses bounded cleanup and relinquishes ownership at its terminal
  result, including when close arrives after STOP has entered `DRAINING`.
  Owner close wins the pending nonterminal stop reason as `OWNER_CLOSED`.
  Explicit release is the terminal-evidence reset point.
- Named host-only fault points cover acquisition, submission copy/commit,
  progress, stop, terminal precommit, cleanup, and release. Every point has a
  deterministic expected-outcome test.
- Tests compare complete before/after state on rejected operations, cover
  boundary values, stale events, competing terminal orders, exact-one
  publication, repeated runs, strict compilation, and available sanitizers.
  Every stable failure reason accepted by the portable failure API has an
  exact state/reason/publication assertion.

## Requirements reinjected by adversarial review

- Owner close during an already-latched STOP drain must replace the pending
  reason with `OWNER_CLOSED`, finish the same one-unit maximum drain, and
  relinquish ownership.
- Test the central terminal-publication guard directly through a host-only
  probe; duplicate public-operation guards are not sufficient proof.
- Exercise every portable failure reason and a table of malformed header,
  reserved, generation, mode, count, divider, flag, symbol, and duration
  inputs, asserting no core mutation on rejection.
- Retain each accepted plan in bounded core-owned storage and prove one logical
  plan release for every terminal cleanup, including cleanup-fault paths.
- RELEASE may relinquish a matching owner after provider death, but it must
  preserve `DEAD / PROVIDER_REMOVED`; neither release nor reacquisition may
  resurrect a dead core.

## Adversarial exit loop

After ordinary checks, separately attempt to falsify ownership, wrap safety,
full-before-commit validation, finite work/drain, transition legality,
first-writer terminal precedence, exactly-one publication, stale rejection,
cleanup latching, route neutrality, and the inert hardware boundary. Perform
targeted mutation challenges for critical generation and terminal guards.
Reinject every objective finding here or in the decision record, correct it,
rerun affected and complete checks, and repeat until no finding remains.

Report exact evidence, skipped checks, safety actions not performed, licensing
and documentation effects, unresolved kernel/target validation, and Git state.
