<!-- SPDX-License-Identifier: MIT -->

# Decision 0012: hybrid permanent Gate D executor

Status: adopted for offline implementation

## Decision

The release ships a candidate-neutral, fail-closed Gate D transaction engine
under `/usr/libexec/rp1-gpclk-dkms/`. The engine owns closed dispatch, command
planning, total deadlines, durable journals, immutable evidence, restart and
new-journal recovery, and composition with the installed lifecycle, boot,
platform, diagnostic, and UAPI tools.

Concrete representative-system instances, target authorization, candidate
identities, the 38-attempt bundle, failure-injection inputs, busy processes,
and captured evidence are qualification assets. They are never installed as
ordinary product runtime data. On a target they may exist only below the
declared Gate D test-owned staging and evidence roots, must be hash-bound before
use, and are removed or retained according to their distinct cleanup and
evidence contracts.

The executor accepts no shell program or arbitrary command. Each external
action must be reproduced by the named permanent subtool's validated planner;
internal actions are a closed typed vocabulary. Root and an explicit execution
flag are required for mutation. Planning and validation remain read-only.

## Candidate consequence

`0.0.0-phase5.13` did not contain this executor and is superseded as a Gate D
candidate. Its source commit, archive, representative builds, route decision,
target plan, attempt work, and authorization records remain immutable
historical evidence for that identity only. They must not be relabeled or
reused for a later candidate.

No successor version is selected by this decision. Version selection and a
new freeze occur only after the permanent executor passes its offline tests and
separate adversarial review. A later candidate requires new release artifacts,
representative builds, route and target inputs, qualification documents, and
fresh target-execution authorization.

## Non-goals

This decision does not authorize target staging, installation, module or
overlay administration, service changes, boot changes, reboot, GPIO, clocks,
DMA, transmission, SDR, or RF. It does not satisfy deferred environmental rows
and does not open publication or consumer integration.
