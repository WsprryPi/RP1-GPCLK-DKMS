<!-- SPDX-License-Identifier: MIT -->

# Current work

The published provider is `1.0.0` / Debian `1.0.0-1`, identified by the immutable
[`v1.0.0` release](https://github.com/WsprryPi/RP1-GPCLK-DKMS/releases/tag/v1.0.0).
Repository documentation and test maintenance can continue without changing
that release's tag, source commit, assets or qualification scope.

The separate
[`qualification-v1.0.0-r1` supplement](https://github.com/WsprryPi/RP1-GPCLK-DKMS/releases/tag/qualification-v1.0.0-r1)
records accepted route evidence for the published software. See the
[qualification metadata procedure](docs/operator/qualification-metadata.md).

## Provider maintenance

Keep the current module, UAPIs, route overlays, runtime management, packaging,
diagnostics and deterministic tests aligned with their maintained contracts.
Build or test a maintenance checkout under its own exact source identity; use
the tagged checkout and published assets when verifying release `1.0.0`.
See the [release procedure](docs/operator/release-candidate.md).

Retain the selected `0.9.0` lifecycle predecessor and package transition matrix.
They are active regression inputs for cleanup-first migration and rollback.
Historical campaign executors and recorded results are not current interfaces.

## Consumer integration

WsprryPi owns production consumption and application acceptance of the
published provider, including installation, cleanup-first migration, activation,
independent GPIO4/GPIO20 routing, operation, removal, rollback and recovery.
Its [release checklist](https://github.com/WsprryPi/WsprryPi/blob/devel/release_tools/Release%20Punchlist.md)
is authoritative for remaining application and operator-documentation work.

Production integration is accepted within the installation, idle-runtime and
qualification-reporting scope of WsprryPi item 10 (RP1 item 18). Installed
GPIO4/GPIO20 status uses the separately pinned supplement; structural
compatibility and application band/mode policy remain independent. The accepted
target rollback exclusion and existing RF qualification scope remain in force.

Use the acceptance matrix and record an applicability rationale when reusing
evidence. Repeat checks affected by changed inputs. Target, service, GPIO,
transmission and RF operations retain their separate authorization and
validation boundaries. Consumer acceptance does not complete the remaining
documentation, final application review or WsprryPi release gates.

A confirmed provider defect requires a scoped provider repair and repetition of
affected checks. Keep module and application changes, releases and qualification
claims separate.

## Release gate cross-reference

Status: ✅ complete within accepted scope · ⏳ in progress · ⬜ not started

| RP1 item | WsprryPi item | Status | Work | Lead repository |
| --- | --- | --- | --- | --- |
| 18 | 10 | ✅ Complete within accepted scope | Published-provider installation, idle runtime and installed qualification reporting | `WsprryPi` |
| 19 | 11 | ⬜ Not started | Documentation performance and Impeccable housekeeping | `WsprryPi-Docs` |
| 20 | 12 | ⬜ Not started | Consolidated operator documentation, including supplement cache, refresh and status | `WsprryPi-Docs` |
| 21 | 13 | ⬜ Not started | Final integrated application Impeccable review (#423) | `WsprryPi` |
| 22 | 14 | ⬜ Not started | 22a / Pi 14a freeze and build; 22b / Pi 14b validate and accept; 22c / Pi 14c publish and verify | `WsprryPi` |

The WsprryPi checklist owns the detailed prerequisites and completion decisions.
RP1 supplies provider-specific support; repository and publication boundaries
remain separate.
