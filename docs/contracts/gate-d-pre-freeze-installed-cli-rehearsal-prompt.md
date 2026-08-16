<!-- SPDX-License-Identifier: MIT -->

# Gate D pre-freeze installed-CLI rehearsal execution prompt

## Objective

Close the process gap that allowed a permanent-executor CLI defect to survive
offline review and reach `wspr5`. Add a mandatory pre-freeze rehearsal that
tests the exact installable Python executor graph and all 38 indexed Gate D
attempts before another successor candidate or control set is generated.

## Verified context

Phase 5.31 completed its corrected output-disabled pre-root transition. Its
first indexed dispatch then failed before `execute()` because a branch-local
import shadowed a module-level name in `main()`. Existing tests separately
covered the state-machine core and installed import authentication, but did not
exercise every attempt through a copied installed CLI.

## Required work

Copy the exact archive-installed executor and its complete local Python module
graph into an isolated temporary install tree. For every hash-indexed attempt,
invoke that copied executor as a process and require successful semantic
validation, a complete fixed plan, and the explicit execute authorization gate
before mutation. Reject tracebacks and lexical import shadowing in `main()`.
Retain the existing stateful fake-system execution of all 38 attempts and the
installed import-graph authentication tests; the new gate complements rather
than replaces them.

Run the focused rehearsal, complete offline suite, whitespace and documentation
checks. Perform a separate adversarial assessment against packaging-path drift,
subprocess-versus-import differences, incomplete attempt coverage, accidental
target mutation, and false claims of authenticated root execution. Correct all
actionable findings and repeat affected checks.

## Constraints and non-goals

Remain offline, unprivileged, network-free, hardware-free, and repeatable. Do
not alter release versions or frozen Phase 5.31 controls. Do not install, load,
bind, activate overlays, change services or boot state, reboot, access GPIO,
enable clocks, submit DMA, operate the separate I2C Si5351 path, use an SDR or
transmitter, connect an antenna, transmit, or produce RF. This rehearsal does
not claim target, kernel, hardware, or RF qualification and does not itself
authorize a Phase 5.32 freeze or execution.

## Exit criteria

All 38 documents pass through the copied installed validation and planning CLI;
all 38 execute invocations stop at the intended pre-mutation authorization
gate without a traceback; the existing 38-attempt fake-system suite and exact
installed-import authentication remain green; the adversarial review has no
unresolved actionable finding; and the complete dirty state is reviewed before
an attributable commit and current-branch push.
