<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 representative-build transfer prompt

## Objective

Determine whether the recorded Phase 5.53 representative build may support the
final product archive without rerunning target compilation, by proving exact
byte identity of the complete kernel/DKMS compilation closure.

## Requirements

1. Compare `Kbuild`, `Makefile`, `dkms.conf`, `include/`, and `src/` between the
   built source commit and final product source commit.
2. Require an empty Git diff for that exact closure.
3. Open the final product archive directly and require every compilation member
   to equal the final commit byte-for-byte.
4. Bind the prior representative-build manifest, target kernel/config/header,
   module output, final product source, and final product archive identities.
5. State that only build evidence transfers. Packaging, qualification tools,
   control paths, authorization, and lifecycle evidence do not transfer.

## Non-goals

No target contact, compilation, DKMS action, installation, control generation,
module or overlay activity, GPIO, clock, DMA, transmission, or RF activity.

## Exit criteria

A deterministic regression independently proves the build closure identical,
and durable evidence limits reuse to the representative build result.
