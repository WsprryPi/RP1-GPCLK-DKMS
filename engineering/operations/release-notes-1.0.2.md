<!-- SPDX-License-Identifier: MIT -->

# RP1-GPCLK-DKMS 1.0.2

Version `1.0.2` / Debian `1.0.2-1` fixes route-manager group provisioning
for installations that do not run Debian package configuration. Earlier
published tags and assets remain unchanged.

## Changes

Neutral activation ensures that the persistent `rp1-gpclk-route` system group
exists before starting the route-manager socket. An existing group retains its
numeric identity and membership. Group creation is verified; failure prevents
socket startup and retains application inhibition for explicit recovery.
Inspection and planning remain read-only. Recovery and removal retain the group.

Offline regressions cover missing and existing groups, creation failure,
verification failure, read-only planning, repeated activation and recovery.
Product, module, controller, DKMS, package, runtime and GPIO4/GPIO20 compatibility
identities use `1.0.2`. Canonical UAPI bytes, overlay sources and kernel resource
behavior are unchanged.

## Installation and support limits

Use the owning workflow to quiesce and remove an earlier provider before a clean
installation. Direct replacement of `1.0.0-1` or `1.0.1-1` and in-place downgrade
are refused. Preserve exact rollback inputs. See the
[package lifecycle contract](package-lifecycle.md).

WsprryPi separately accepts and selects a tagged provider. This release does not
change its pinned provider, application policy or qualification evidence. The
compatibility manifest defaults to `Unavailable` with no target entries.
Source/package reproducibility and offline tests do not establish target
installation, binding, timing, GPIO, transmission, RF or product qualification.
Existing scoped evidence remains bound to its exact software and conditions.
Licensing and repository ownership boundaries are unchanged.

The [release procedure](release-candidate.md) defines the seven reproducible
assets, independent validation and immutable publication checks.
