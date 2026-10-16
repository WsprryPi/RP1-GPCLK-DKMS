<!-- SPDX-License-Identifier: MIT -->

# Roadmap

Status: ✅ complete · ⏳ in progress · ⬜ not started

1. ✅ Reconcile the DKMS development contract.
2. ✅ Implement the guarded WsprryPi development policy.
3. ✅ Establish the Qualification Harness workflow.
4. ✅ Integrate the module and reconcile Issue #412.
5. ✅ Repair, deploy, and verify the development stack.
6. ✅ Test all WsprryPi modes on GPIO4 and GPIO20.
7. ✅ Enable rebootless GPIO4/GPIO20/none switching.
8. ✅ Exercise the complete WsprryPi product path.
9. ✅ Define Raspberry Pi 5 compatibility and mode ownership.
10. ✅ Normalize the development version to 0.9.0.
11. ✅ Clean historical publication and repository material.
12. ✅ Implement product improvements.
13. ✅ Assess and apply only justified hardening.
14. ✅ Build the canonical 1.0.0 release candidate.
15. ✅ Validate the package lifecycle and 0.9-to-1.0 upgrades.
16. ✅ Accept the exact DKMS candidate against current WsprryPi `devel`.
17. ✅ Integrate the accepted DKMS provider repair and WsprryPi consumer
    branches, repeat affected acceptance checks, then freeze and publish the
    immutable DKMS 1.0.0 release.
18. ⬜ **Published-provider integration and acceptance planning.**
    **Lead: `WsprryPi` · WsprryPi item 10.** Before implementation, define the
    supported platform/backend/route acceptance matrix, required software,
    installation, service and runtime evidence, exact identities, reusable
    evidence, accepted exclusions and limitations, and separately authorized
    target checks. Consume and verify the published immutable DKMS 1.0.0
    identities through production selection while preserving supported
    development selectors and fail-closed behavior. Validate installation,
    cleanup-first migration, runtime activation, GPIO4/GPIO20 routing,
    operation, removal, rollback, diagnostics and recovery. Reuse accepted
    evidence only with a recorded applicability rationale and repeat checks
    affected by changed inputs. Reconcile stale publication statements in
    WsprryPi maintainer documentation and issue #412, and record operator-
    documentation impacts for item 20. Before item 21, resolve the #412/#423
    sequencing conflict by explicitly permitting publication-only tracking to
    remain open once its implementation and integration prerequisites are
    accepted, while preserving #412's final publication closeout requirement;
    do not claim that the GitHub criteria have already changed.
19. ⬜ **Documentation performance and remaining Impeccable housekeeping.**
    **Lead: `WsprryPi-Docs` · WsprryPi item 11.** Reconcile saved image-
    optimization, product-metadata and host/tooling reminders. Complete
    justified documentation performance and presentation work before final
    rendering and screenshots. Use Impeccable for subsequent UI work;
    application UI repairs belong in WsprryPi and must settle before item 21.
20. ⬜ **Consolidated operator documentation.**
    **Lead: `WsprryPi-Docs` · WsprryPi item 12.** Incorporate item 18's
    documentation impacts. Cover the settled API and Phase 15.4 resources,
    Test Tone, calibration boundaries, Si5351 disposition/drive/fade,
    inventory timeout, and RP1 correction, installation, migration and
    recovery. Align support claims with the acceptance matrix, build and render
    the documentation, verify links, and replace materially inaccurate
    screenshots.
21. ⬜ **Final integrated application Impeccable review (#423).**
    **Lead: `WsprryPi` · WsprryPi item 13.** Begin after items 18–20 and
    release-scoped implementation are accepted on their respective integrated
    branches, with the application candidate on `devel` and no expected UI-
    affecting changes. Confirm that the publication-only tracking exception is
    reflected in the issue criteria. Review the complete application, repair
    actionable findings, explicitly disposition accepted findings, and repeat
    affected tests and visual checks. Coordinate only affected documentation
    and screenshot repairs with WsprryPi-Docs. Record the exact reviewed
    application and documentation identities before packaging.
22. ⬜ **Final WsprryPi candidate and 4.0 publication.**
    **Lead: `WsprryPi` · WsprryPi item 14.** Complete these checkpoints in
    order:

    - ⬜ **22a / Pi 14a — Freeze identities and build artifacts.** After item
      21, settle version metadata, release notes, compatibility requirements
      and known limitations. Record exact application/documentation commits
      and provider identities; build and checksum the release artifacts.
    - ⬜ **22b / Pi 14b — Validate the exact candidate and obtain acceptance.**
      Run required CI/regressions and applicable installation, upgrade, service
      and runtime checks against frozen source and actual release artifacts
      using the acceptance matrix. Record reused evidence, repeated checks,
      exclusions and limitations. Repair findings and reassess. Changes after
      freeze require updated candidate identities and repetition of affected
      checks, including UI/documentation review when applicable.
    - ⬜ **22c / Pi 14c — Publish and independently verify.** After acceptance
      and publication authorization, publish WsprryPi 4.0 and the corresponding
      operator-documentation revision through separate workflows. Verify the
      published tag and commit identities, downloads, checksums and
      documentation availability, then complete release-tracking closeout,
      including #412.

## Remaining work ownership and cross-reference

| RP1 item | WsprryPi item | Status | Work | Lead repository |
| --- | --- | --- | --- | --- |
| 18 | 10 | ⬜ Not started | Published-provider integration and acceptance planning | `WsprryPi` |
| 19 | 11 | ⬜ Not started | Documentation performance and Impeccable housekeeping | `WsprryPi-Docs` |
| 20 | 12 | ⬜ Not started | Consolidated operator documentation | `WsprryPi-Docs` |
| 21 | 13 | ⬜ Not started | Final integrated application Impeccable review | `WsprryPi` |
| 22 | 14 | ⬜ Not started | 22a freeze/build; 22b validate/accept; 22c publish/verify | `WsprryPi` |

The lead repository owns coordination and completion evidence. WsprryPi leads
production integration, final application review and release. WsprryPi-Docs
leads documentation performance and operator documentation. RP1 supplies
provider-specific support; a confirmed provider defect requires its own scoped
repair and repetition of affected qualification. Keep repository changes and
publication boundaries separate.

Items 18–22 do not reopen deferred calibration experiments, macOS #411/#419
work, Standard Feld or Pico P15.5.
