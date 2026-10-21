<!-- SPDX-License-Identifier: MIT -->

# Current work

The published provider is `1.0.0` / Debian `1.0.0-1`, identified by the immutable
[`v1.0.0` release](https://github.com/WsprryPi/RP1-GPCLK-DKMS/releases/tag/v1.0.0).
WsprryPi bundles pinned scoped route evidence locally; no separate
qualification release is consumed. See
[qualification metadata](engineering/operations/qualification-metadata.md)
for applicability and exclusions.

## Provider maintenance

Keep the module, UAPIs, route overlays, runtime management, packaging,
diagnostics and deterministic tests aligned with their maintained contracts.
Build or test a maintenance checkout under its own exact source identity; use
the tagged checkout and published assets when verifying release `1.0.0`.
See the [release procedure](engineering/operations/release-candidate.md).

Retain the selected `0.9.0` lifecycle predecessor and package transition matrix.
They are active regression inputs for cleanup-first migration and rollback.
A confirmed provider defect requires a scoped repair and affected checks.
Target, service, GPIO, transmission and RF operations retain their separate
authorization and validation boundaries.

## Consumer work and ownership

WsprryPi owns application acceptance, installation orchestration, migration,
activation, independent GPIO4/GPIO20 operation, removal, rollback and recovery.
Its [release checklist](https://github.com/WsprryPi/WsprryPi/blob/devel/release_tools/Release%20Punchlist.md)
owns selected application and operator-documentation work. RP1 supplies
provider-specific support. Keep module and application changes, releases and
qualification claims separate.

The selected work below is RP1 item 22 / WsprryPi item 16. WsprryPi owns
candidate coverage for its Pico WSPR Type 2/3 management integration and
independent valid-field saves (Pi items 14–15). They have no separate RP1 item
numbers; broader Pico documentation and physical qualification remain separate.

## Item 22 / WsprryPi item 16 — Beta 1 milestone

⏳ **WsprryPi 4.0 Beta 1 release documentation and candidate preparation.**
WsprryPi 16 · Lead: `WsprryPi`. Release-note drafting and replacement candidate
acceptance (22a–22c / Pi 16a–16c) are complete within their application-owned
scope. Publication and announcements (22d–22e / Pi 16d–16e) remain not started
and require separate authorization. Final WsprryPi 4.0 stable publication is
outside this milestone.

### Publication prerequisites and acceptance limits

The WsprryPi checklist, candidate manifest and release evidence own the exact
executable, supporting installer/UI, documentation, provider and bundled
evidence identities. Keep these requirements with the publication work:

- Refreeze supporting installer/helper inputs affected by local evidence
  installation and repeat affected installation/status acceptance. Preserve
  the published provider and the accepted executable and RF scopes.
- Refresh WsprryPi's `release_tools/4.0-Beta-1-Release-Notes.md` and companion
  `release_tools/4.0-Beta-1-Release-Evidence.md` against the exact publication
  inputs. Reconcile the stable-to-Beta source inventory, readiness and relevant
  closed-issue dispositions, commit/merge history and internal evidence;
  issue closure or readiness alone does not prove a change shipped.
- Use the four replacement exports identified by WsprryPi's candidate manifest
  for executable source `1e047a44`. Distinguish frozen executable source from
  accepted supporting installer/UI source. Preserve accepted documentation,
  published provider and pinned evidence byte identities. Changed artifacts
  or acceptance assertions require updated identities and affected checks.
- Keep acceptance bounded to the documented executable replacement/restart and
  idle-runtime cases and explicit reuse of unchanged normal-installer/UI
  acceptance. Fresh clean installation, the other three exports on physical
  targets, reboot and fresh GPIO4 selection remain accepted unperformed checks.
  Carry forward the documented service-request cap exception as an exception,
  never a passing budget check or retroactive authorization.
- Preserve the exact identities, finite limits and applicability of reused
  provider, route, qualification and recovery evidence. Earlier RP1 and Pi
  items 10–15 do not automatically qualify changed inputs. Candidate acceptance
  establishes neither publication nor general hardware/RF qualification.

### Remaining release gates

- ⬜ **22d / Pi 16d — Later: Publish Beta 1 as a GitHub prerelease and verify.**
  After separate publication authorization, reconcile the complete publication
  packet with the accepted executable, supporting installer/UI and documentation
  identities. Do not substitute a newer branch head or omit accepted support
  repairs. Recheck required CI and refresh affected source, asset, documentation
  and release-note links. Publish the accepted candidate and corresponding
  documentation through their separate workflows, using the reviewed Markdown
  body and prerelease classification. Independently verify tag/source identities,
  downloads, checksums, release notes and documentation availability. This is not
  final WsprryPi 4.0 stable publication.
- ⬜ **22e / Pi 16e — After publication: Update every open ready-for-release
  issue.** Only after Beta 1 publication is independently verified, freshly
  enumerate every open issue marked ready for release using the actual readiness
  markers and complete pagination. Reconcile each issue against the shipped
  scope and update it with the verified prerelease URL and accurate availability
  and testing guidance. Do not imply an unshipped fix is included. Preserve
  issue states, avoid duplicate comments, and record coverage, comment URLs
  and failures. Resolve failed or omitted updates before declaring this
  checkpoint complete.

Revisit only affected acceptance when a confirmed defect, changed input or
publication discrepancy invalidates its earlier result. Later provider maintenance
and legacy client fixes do not replace the frozen `1.0.0` software or broaden
the pinned route evidence. Preserve the software publication, evidence source
identities and accepted qualification limits. This plan grants no
installation, hardware/RF operation, candidate rebuild, release-branch merge,
tag, release/draft, asset upload, publication or issue announcement.
