<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.23 pre-root transition adversarial assessment

Status: offline implementation review passed; candidate not frozen

Phase 5.23 separates the one-shot pre-root authority from normal root-bound
dispatch. The staged outer executor verifies the explicitly supplied envelope
hash, its own staged identity, and the pre-root module bytes before compiling
that module. The transition then verifies every staged input, requires an
absent destination below a real owner-matched parent, creates the mode-0700
root and immutable marker, dispatches exact install and cleanup vectors,
copies only bound control documents, verifies installed tools and the empty
output-disabled baseline, and commits its external journal. Replay fails once
the root exists.

Stateful filesystem tests cover success, replay, malformed candidate and root
identities, swapped markers, missing, stale, substituted, and symlinked inputs,
unsafe parents, traversal, live-output injection, baseline mismatch, installed
tool substitution, retained residue, and interruption plus recovery at every
nonterminal durable checkpoint.

The second adversarial pass found and closed two additional issues: the archive
hash is now tied to one exact staged archive path, and the install, cleanup,
and recovery vectors are pinned to authenticated administrator and lifecycle
operations. Parent permissions and the final root owner, mode, marker, installed
tools, copied documents, residue set, and output-disabled baseline are all
rechecked before commit.

The complete offline suite passed twice. Two development builds from the final
dirty working tree were byte-identical, with provisional archive SHA-256
`02378ded1e620bbc168b1e2697728d7e715d1f4a6bda9450aba29deec8ee1838`.
This is reproducibility evidence only: the candidate cannot be frozen until
the reviewed changes are committed and two clean builds bind that exact source
commit. No target evidence is claimed.
