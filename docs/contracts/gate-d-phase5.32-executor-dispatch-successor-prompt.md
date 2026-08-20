<!-- SPDX-License-Identifier: MIT -->

# Phase 5.32 executor-dispatch successor execution prompt

Create a distinct successor candidate to preserve the immutable Phase 5.31
candidate, corrected control set, committed qualification root, installed
tools, authorization, and failed first dispatch. Phase 5.31 completed its
output-disabled pre-root transition, but attempt 1 stopped before its first
operation because a branch-local `import sys` in `gate_d_outer.main()` shadowed
the module binding used by the execute branch.

Keep the implementation correction minimal: remove the redundant local import
and add a subprocess regression that enters the actual execute CLI branch and
reaches its explicit root/argument authorization gate without an
`UnboundLocalError`. Audit other CLI branches for the same lexical-binding
class. Do not weaken root, instance, index, document-hash, route, deadline,
immutable-evidence, inactive-terminal-state, or output-disabled checks.

Record the Phase 5.31 corrected bootstrap success and pre-operation dispatch
failure durably. Run focused tests, the complete offline suite, whitespace and
documentation checks, and a separate adversarial review. Correct every
actionable finding and repeat affected checks.

After the repair is committed and the worktree is clean, freeze a new successor
from that exact commit. Produce two isolated byte-identical release builds and
an exact build-only representative compile on `wspr5`. Then generate a wholly
new route decision, target plan, 38-attempt bundle, execution instance,
pre-root envelope, and complete Gate D control set with successor-specific
paths and hashes. Independently validate the entire graph, including execution
of every permanent-executor CLI branch through its pre-mutation gate.

Do not patch the installed Phase 5.31 tool or qualification root. Do not reuse
its authorization. Until fresh explicit authorization is recorded, do not
install the successor, load or bind a module, activate an overlay, change
services or boot state, reboot, access GPIO, enable clocks, submit DMA, operate
the separate I2C Si5351 output path, touch a transmitter or SDR, connect an
antenna, transmit, or produce RF. Do not tag, publish, open a pull request, or
modify dependent repositories.
