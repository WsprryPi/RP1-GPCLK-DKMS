<!-- SPDX-License-Identifier: MIT -->

# Current work

The published provider is `1.0.0` / Debian `1.0.0-1`, identified by the immutable
[`v1.0.0` release](https://github.com/WsprryPi/RP1-GPCLK-DKMS/releases/tag/v1.0.0).
Repository documentation and test maintenance can continue without changing
that release's tag, source commit, assets or qualification scope.

## Provider maintenance

Keep the current module, UAPIs, route overlays, runtime management, packaging,
diagnostics and deterministic tests aligned with their maintained contracts.
Build or test a maintenance checkout under its own exact source identity; use
the tagged checkout and published assets when verifying release `1.0.0`.
See the [release procedure](engineering/operations/release-candidate.md).

Retain the selected `0.9.0` lifecycle predecessor and package transition matrix.
They are active regression inputs for cleanup-first migration and rollback.
Historical campaign executors and recorded results are not current interfaces.

## Consumer integration

WsprryPi owns production consumption and application acceptance of the
published provider, including installation, cleanup-first migration, activation,
independent GPIO4/GPIO20 routing, operation, removal, rollback and recovery.
Its [release checklist](https://github.com/WsprryPi/WsprryPi/blob/devel/release_tools/Release%20Punchlist.md)
is authoritative for remaining application and operator-documentation work.

Define the applicable acceptance matrix and identify reused evidence with an
applicability rationale. Repeat checks affected by changed inputs. Target,
service, GPIO, transmission and RF operations retain their separate authorization
and validation boundaries. Provider publication or source cleanup does not
complete those consumer gates.

A confirmed provider defect requires a scoped provider repair and repetition of
affected checks. Keep module and application changes, releases and qualification
claims separate.
