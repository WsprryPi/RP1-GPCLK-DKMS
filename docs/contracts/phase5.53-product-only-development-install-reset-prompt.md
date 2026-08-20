<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 product-only development-install reset prompt

## Objective

Stop using the Gate D qualification bootstrap as the deployment mechanism.
Add one explicit product-only development-candidate installation mode to the
existing administrator so an unpublished candidate can be installed through
the same DKMS lifecycle as a published product without the qualification
archive, qualification identity, pre-root envelope, execution instance, or
attempt graph.

## Requirements

- `install --execute --allow-development --release-directory RELEASE --route
  gpio4|gpio20` accepts only a checksum-valid, non-publishable development
  release and uses no qualification inputs.
- Ordinary published installation remains unchanged and does not require the
  new flag.
- Qualification installation remains a separate legacy qualification path;
  combining it with `--allow-development` fails closed.
- The development path retains the existing transaction journal, exact product
  inventory, DKMS add/build/install sequence, inactive overlay installation,
  signing checks, rollback behavior, and `live_output=0` ceiling.
- Update operator documentation and deterministic tests. Do not regenerate an
  archive, contact a target, install a module, apply an overlay, or perform any
  hardware activity in this slice.

## Exit criteria

Offline tests must prove that product-only development installation excludes
the qualification archive and qualification identity, rejects ambiguous flag
combinations, and preserves the existing published and qualification paths.
