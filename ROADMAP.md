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
| 19 | 11 | ✅ Complete within accepted scope | Documentation performance and Impeccable housekeeping | `WsprryPi-Docs` |
| 20 | 12 | ⏳ In progress | Consolidated operator documentation, including supplement cache, refresh and status | `WsprryPi-Docs` |
| 21 | 13 | ⬜ Not started | Final integrated application Impeccable review (#423) | `WsprryPi` |
| 22 | 14 | ⬜ Not started | WsprryPi 4.0 Beta 1 release documentation and candidate preparation; stop after 22c / Pi 14c; later publication and issue updates under 22d–22e / Pi 14d–14e | `WsprryPi` |

The WsprryPi checklist owns the detailed prerequisites and completion decisions.
RP1 supplies provider-specific support; repository and publication boundaries
remain separate.

## Item 22 / WsprryPi item 14 — Beta 1 milestone

⬜ **WsprryPi 4.0 Beta 1 release documentation and candidate preparation.**
WsprryPi 14 · Lead: `WsprryPi`. Current preparation stops after **22c / Pi 14c**.
Final WsprryPi 4.0 stable publication is outside this Beta 1 milestone.

Release-note research and drafting may run alongside WsprryPi items 12–13
(RP1 items 20–21). Candidate freeze/build and acceptance follow the integrated
application review in WsprryPi item 13 (RP1 item 21).

- ⬜ **22a / Pi 14a: Research and draft Beta 1 release documentation in
  Markdown.** Establish the previous published stable baseline and intended
  stable-to-Beta source range. Discover the actual readiness labels, project
  statuses and milestones; completely enumerate all issues marked ready for
  release and closed issues relevant to that range, including pagination.
  Reconcile inclusion against commit/merge history and relevant internal
  documentation and evidence. Closure or readiness alone does not prove that
  a change shipped. Plan these WsprryPi deliverables:
  `release_tools/4.0-Beta-1-Release-Notes.md` and
  `release_tools/4.0-Beta-1-Release-Evidence.md`. The public Markdown must suit
  the eventual GitHub prerelease body and cover added/changed/fixed behavior,
  removals/deprecations, confirmed compatibility breaks and risks, operator
  migration/rollback actions, dependencies and known limitations. The companion
  records issue/commit/evidence coverage, exclusions and unresolved claims.
  Refresh the notes against the accepted candidate before publication. These
  files belong in WsprryPi; this roadmap update does not create them or perform
  the research.
- ⬜ **22b / Pi 14b: Freeze identities and build the Beta 1 candidate.** After
  the integrated application review, settle Beta 1 version metadata and record
  exact application/documentation commits and published provider/supplement
  identities. Build and checksum the candidate artifacts. Preserve the researched
  comparison range. Changes after freeze require updated candidate identities
  and repetition of affected acceptance checks, including UI/documentation
  review where applicable.
- ⬜ **22c / Pi 14c: Validate, accept and hand off; stop before publication.**
  Run required CI/regressions and applicable installation, upgrade, service and
  runtime checks against the exact candidate and artifacts using the acceptance
  matrix. Record reused evidence, repeated checks, exclusions and accepted
  limitations; repair findings and reassess. Reconcile the release notes and
  compatibility guidance with the tested result. Hand off accepted identities,
  checksums, the Markdown prerelease body and supporting evidence. Stop before
  release-branch integration, tagging, GitHub release/draft creation, asset
  uploads or availability announcements. Candidate acceptance does not establish
  publication.
- ⬜ **22d / Pi 14d — Later: Publish Beta 1 as a GitHub prerelease and verify.**
  Only after separate publication authorization, publish the accepted candidate
  using the reviewed Markdown body and mark the release as a prerelease.
  Independently verify tag/source identities, downloads, checksums, release
  notes and corresponding documentation availability through their separate
  workflows. This is not final WsprryPi 4.0 stable publication.
- ⬜ **22e / Pi 14e — After publication: Update every open ready-for-release
  issue.** Only after Beta 1 publication is independently verified, freshly
  enumerate every open issue marked ready for release using the actual readiness
  markers and complete pagination. Reconcile each issue against the shipped
  scope and update it with the verified prerelease URL and accurate availability
  and testing guidance. Do not imply an unshipped fix is included. Preserve
  issue states, avoid duplicate comments, and record coverage, comment URLs
  and failures. Resolve failed or omitted updates before declaring this
  checkpoint complete.

All checkpoints remain not started. This checklist/documentation update
authorizes no release preparation or execution, research, builds, tagging,
release/draft creation, asset uploads, publication or issue announcements.
Checkpoints 22a–22c describe the preparation scope for a separately authorized
execution; 22d–22e are later gates. RP1's published `1.0.0` release,
`qualification-v1.0.0-r1` supplement, immutable identities and accepted
qualification limits remain unchanged.
