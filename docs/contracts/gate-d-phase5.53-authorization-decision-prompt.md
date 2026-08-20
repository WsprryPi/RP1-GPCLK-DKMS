<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 digest-bound output-disabled authorization decision prompt

The operator may authorize only the exact Phase 5.53 Gate D control set bound
by all of these identities:

- control-set commit: `2838380a639d7af71ddc53be20829efd56cedc1d`;
- product source: `1884c0f1c53c661495576bf10ce08d8bf7a90bc3`;
- product archive SHA-256:
  `ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549`;
- qualification source: `834d05c5c5da0c383c4a229eaeff9dae07a4359b`;
- qualification archive SHA-256:
  `d931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0`;
- accepted construction snapshot SHA-256:
  `df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7`;
- preauthorization execution-instance SHA-256:
  `0cb6d2744b20ba5aa412df0702abe230e38b1e407db1c5bd31bfc36c976ac7f1`;
- schema-6 pre-root envelope SHA-256:
  `e9865ebd6208aa4dac1ee60a9b0715936cef1d60b9357b9bdce370343c0087ac`;
- 38-attempt index SHA-256:
  `3a6a6047dc8e3ca5c77488a5029bb2165f5b9e71bf32fdc94ec60dcf15ec15e2`;
- control construction evidence SHA-256:
  `ef3f074a0e05f78485a9f1e505f302f5fa6adfb900347f2218651cd076effda1`;
- successor release-input inventory SHA-256:
  `b3ae7d71aa1eb8881450b068f9c3525ecf33925ab797419c735b9f4f5aca18cb`;
- predecessor package inventory SHA-256:
  `17220ae534936e55fc1710edcd8cebff88add93adb82bd607e020714569a175d`;
- qualification-install identity SHA-256:
  `c4bdf3e066527941e5762229d0162b738bea542ec8d47a2cdfda0e66ef7a0ebb`.

Authorization is limited to the 38 indexed schema-2 attempts in the ten ready
rows, namespace `phase5.53-1884c0f1c53c`, the exact eight release inputs, the
snapshot-derived 28-path Phase 5.52 predecessor inventory, the frozen Phase
5.53 successor inventory, and the authenticated schema-6 pre-root, ledger
archival, recovery, service, stock-kernel, DKMS, overlay, load-disabled, query,
unbind/rebind, unload, bounded failure-injection, and cleanup operations sealed
in those controls. The five deferred environmental rows remain excluded.

An explicit authorization first permits only a read-only canonical `wspr5`
recapture using the already reviewed snapshot tool streamed directly into
privileged Python. It may inspect the declared kernel, headers, package paths,
terminal administrator state, six service states, inactive module/endpoint/
overlay/DKMS state, and declared physical-safety state. It may not mutate the
target. The two new captures must be byte-identical to one another and must
match every execution-relevant field and identity bound by the accepted
construction snapshot. Any difference invalidates the authorization before
staging.

The required baseline is six reviewed services inactive; module and endpoint
absent; no route overlay or test DKMS version; terminal-complete Phase 5.52
administrator state; exact predecessor paths and kernel identities;
authenticated recovery; unused SDR; no antenna; and the separate I2C Si5351
path disconnected and unused. Any missing, duplicate, active, changed, or
inconsistent state fails closed.

Only after an exact recapture may the execution instance be regenerated to
change `approved`, `targetExecutionApproved`, approval-scope, execution-ready
state, and dependent hashes. Independently validate the complete regenerated
graph and exact archived product-plus-qualification input closure, then commit
and push those authorized bytes before target staging. Do not combine the
recapture/authorization commit with staging or the pre-root transition.

If authorized controls are later staged, execution must use only the
authenticated pre-root transition, sealed-root policy and module graph, and
installed permanent tools. Stop on the first identity, state, timeout,
service, recovery, residue, cleanup, transition, or safety discrepancy. Use
only journal-authorized recovery. Terminal pre-root recovery must return
without starting an attempt.

Output remains disabled. Active pinctrl, clock enablement, DMA submission,
GPIO output, Si5351 operation, transmitter keying, SDR operation, antenna
connection, RF, `/dev/mem`, custom-kernel qualification, forced removal,
general upgrade, and unreviewed persistent boot mutation are prohibited.

The exact authorization phrase is:

> I explicitly authorize the exact Phase 5.53 control set at commit
> 2838380a639d7af71ddc53be20829efd56cedc1d, beginning with the bounded
> read-only byte-identical preauthorization recapture and, only if it matches,
> regeneration and commit of the authorized offline controls. I do not yet
> authorize target staging or the pre-root transition.

This prompt does not itself record authorization. Until the operator supplies
that exact authorization, keep `approved: false`,
`targetExecutionApproved: false`, and `executionReady: false`; do not connect
to the target, recapture it, stage inputs, or begin the pre-root transition.
