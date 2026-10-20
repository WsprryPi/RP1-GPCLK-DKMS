<!-- SPDX-License-Identifier: MIT -->

# Current work

The published provider is `1.0.0` / Debian `1.0.0-1`, identified by the immutable
[`v1.0.0` release](https://github.com/WsprryPi/RP1-GPCLK-DKMS/releases/tag/v1.0.0).
The separately identified `qualification-v1.0.0-r1` supplement records scoped
route evidence. See [qualification metadata](engineering/operations/qualification-metadata.md)
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

The selected work below is RP1 item 22 / WsprryPi item 16. WsprryPi items 14
and 15 cover the accepted Pico WSPR Type 2/3 management integration and
independent valid-field saves. They have no separate RP1 item numbers. Their
selected Pi/Beta adoption and affected validation are covered by the candidate
acceptance; broader Pico documentation and physical qualification retain their
separate scope.

## Item 22 / WsprryPi item 16 — Beta 1 milestone

⏳ **WsprryPi 4.0 Beta 1 release documentation and candidate preparation.**
WsprryPi 16 · Lead: `WsprryPi`. Preparation through **22c / Pi 16c** is complete
within its accepted scope. Publication and announcements in 22d–22e / Pi
16d–16e remain not started and require separate authorization. Final WsprryPi
4.0 stable publication is outside this Beta 1 milestone.

The WsprryPi checklist, candidate manifest and release evidence are authoritative
for the exact executable, supporting installer/UI, documentation, provider and
supplement identities. Completed RP1 acceptance and WsprryPi items 10–15 retain
their recorded scopes; they do not automatically qualify later changed inputs.

- ✅ **22a / Pi 16a: Research and draft Beta 1 release documentation in
  Markdown.** Complete. The stable-to-Beta source inventory, ready-for-release
  and relevant closed-issue dispositions, commit/merge history and internal
  evidence are reconciled in WsprryPi's
  `release_tools/4.0-Beta-1-Release-Notes.md` and
  `release_tools/4.0-Beta-1-Release-Evidence.md`. Refresh the public notes and
  companion coverage against the exact publication inputs; closure or readiness
  alone does not prove that a change shipped.
- ✅ **22b / Pi 16b: Freeze identities and build the Beta 1 candidate.**
  Complete for the four exports identified by WsprryPi's candidate manifest.
  Preserve the distinction between frozen executable source and accepted
  supporting installer/UI source. Use the exact accepted documentation and
  unchanged published provider/supplement identities. Changes affecting an
  artifact or acceptance assertion require updated identities and repetition
  of affected checks before publication.
- ✅ **22c / Pi 16c: Validate, accept and hand off; stop before publication.**
  Accepted for the recorded software, finite wspr5 upgrade/repeat-installation,
  idle runtime and affected UI scope. Fresh clean installation, the other three
  exports on physical targets, reboot and fresh GPIO4 selection remain explicitly
  accepted unperformed checks. Preserve the documented operator-accepted
  service-request cap exception: 20 requests occurred against an approved 18;
  this is neither a passing budget check nor retroactive authorization. Reused
  provider, route, qualification and recovery evidence retains its original
  identity and applicability. Candidate acceptance does not establish Beta
  publication or general hardware/RF qualification.
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
the `qualification-v1.0.0-r1` supplement. Preserve both publications and their
accepted qualification limits. This roadmap reconciliation authorizes no
installation, hardware/RF operation, candidate rebuild, release-branch merge,
tag, release/draft, asset upload, publication or issue announcement.
