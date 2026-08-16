<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.21 control-set construction adversarial assessment

Status: blocked before target-plan construction

## Intended slice

The slice attempted to construct the exact Phase 5.21 qualification root,
bootstrap plan, route decision, version pair, schema-4 target plan,
schema-2 38-attempt index, attempt documents, and schema-3 execution instance.
It was offline-only and authorized no Raspberry Pi contact or mutation.

## Blocking finding

The frozen administrator installs the permanent Python entry points under
hyphenated command names such as `gate-d-bootstrap`, `gate-d-instance`,
`gate-d-target-plan`, and `gate-d-attempts`. The permanent executor imports
those dependencies by the underscore module names `gate_d_bootstrap`,
`gate_d_instance`, `gate_d_target_plan`, and `gate_d_attempts`. Those module
files do not exist in the installed `/usr/libexec/rp1-gpclk-dkms` layout, and
the executor does not authenticate and add the qualification-root `scripts`
directory to `sys.path` for those imports.

The first bootstrap dispatch therefore fails before plan validation or
mutation with:

```text
ModuleNotFoundError: No module named 'gate_d_bootstrap'
```

The defect was reproduced from the exact Phase 5.21 source by placing
`gate_d_outer.py`, `gate_d_bootstrap.py`, and `gate_d_root.py` under their
administrator-installed names and invoking the installed-name executor's
read-only bootstrap-validation path. Exit status was 1. The pre-import
root-validator test did not detect this because it loaded the executor from a
qualification-root source path and stopped after authenticating
`gate_d_root`; it did not dispatch a subordinate import from the installed
layout.

## Security and lifecycle consequence

Adding unbound files, setting `PYTHONPATH`, invoking from a source checkout, or
copying modules ad hoc would bypass the frozen installation inventory and
tool identities. None is an acceptable workaround. The bootstrap cannot
establish the reviewed permanent-tool transition, so a truthful schema-4
target plan, 38-attempt bundle, or ready execution instance must not be sealed
for Phase 5.21.

## Required successor correction

A distinct successor must close the complete installed Python import graph.
It should install authenticated importable module files separately from the
operator command entry points, bind every installed module identity in the
release inventory and target plan, and test bootstrap plus normal executor
dispatch from an exact installed-layout directory outside a checkout. Tests
must cover missing, swapped, stale, symlinked, and post-bootstrap-substituted
subordinate modules as well as the root validator.

Only after that successor passes offline adversarial review, deterministic
freeze, and a separately authorized representative build may Gate D control
set construction resume.

## Activity boundary

No Raspberry Pi was contacted or changed. No installation, DKMS, module,
overlay, service, boot, reboot, GPIO, clock, DMA, Si5351, SDR, transmission,
antenna, or RF activity occurred.
