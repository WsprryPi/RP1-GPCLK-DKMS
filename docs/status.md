<!-- SPDX-License-Identifier: MIT -->

# Read provider status

Use WsprryPi's route controls for everyday status. Detailed facts are available
through the [installed command-line tools](command-line.md) or a support
bundle. The detailed RP1 fact panel may be hidden in the normal Setup view.

## Route facts

| Fact | Meaning |
| --- | --- |
| Requested | The route in the current draft or transaction request |
| Persisted | The RP1 route saved in WsprryPi configuration |
| Configured | The route reported by managed administration |
| Active | The route reported by the loaded provider |
| Eligible | Current application checks admit the requested operation |

WsprryPi blocks transmission when required route facts disagree or readiness
cannot be proved. A retained GPIO setting for another backend is not RP1 route
consent. `eligible=false` in an observational response does not by itself mean
a band is unavailable; no specific application plan may have been evaluated.

## Runtime provider results

`runtime_provider.py inspect` uses the following result and process exit codes.
Nonzero codes can describe an expected incomplete installation, not just a
failed command.

| Result | Exit | What to do |
| --- | ---: | --- |
| `neutral_ready` | 0 | Administration is ready with no consumer route. Select a route when needed. |
| `exact_ready` | 0 | The exact owned runtime has one aligned route and verified idle state. Use WsprryPi for operation checks. |
| `absent` | 10 | No runtime installation is present. Use the WsprryPi installer if RP1 is intended. |
| `deployment_required` | 11 | Filesystem deployment is incomplete. Review the installer result. |
| `recovery_required` | 12 | A transaction or restoration record needs its owning recovery operation. Preserve records. |
| `conflict` | 13 | Identity, ownership or state is unsafe, mixed or contradictory. Stop and investigate. |
| `activation_required` | 14 | Files are deployed but managed neutral activation remains. Use the owning installer/startup workflow. |

These describe an idle readiness inspection. A running operation may have an
owner and open endpoint; collect status in context and do not attempt recovery
merely because an idle-readiness check cannot admit active state.

## Compatibility, qualification and output

**Structural compatibility** describes the provider's recognized resources.
`Compatible-unqualified` does not erase separately established application
qualification. `Experimental` identifies development scope; it is not a
release or RF approval. `Unavailable`, `Rejected` or an unknown state requires
the accompanying reason before further operation.

**Qualification evidence** describes a particular software, route and test
scope. The original v1.0.0 compatibility manifest is empty with a default of
`Unavailable`; the separate qualification supplement does not rewrite it.
Missing or invalid supplemental evidence is an evidence problem and must not
be converted into an invented application band restriction.

**Operational readiness** describes current resources, ownership, cleanup and
inhibition. The production module's `output_inhibit=0` means submissions can
be considered through the root-only endpoint; it does not mean that output is
currently active. `output_inhibit=1` is an immutable load-time development gate
that rejects submission. Do not change it as a troubleshooting shortcut.

Passive observations can be **true**, **false** or **unknown**. Unknown is never
converted into safe. Lease or owner presence, a cleanup fault or a pending
transaction must be resolved through its owning workflow.
