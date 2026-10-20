<!-- SPDX-License-Identifier: MIT -->

# Documentation maintenance

`docs/` is the published operator handbook. Keep current capabilities,
prerequisites, procedures, support limits and troubleshooting there. Technical
contracts, build and packaging procedures and developer workflows belong in
`engineering/`. Update repository references and package-source mappings when
moving a technical document; retained files can be current build inputs.

## Scaffold and provenance

The handbook uses the Sphinx/MyST/Read the Docs theme scaffold from
[WsprryPi-Docs](https://github.com/WsprryPi/WsprryPi-Docs). Its navigation groups,
typography, colors, logo, favicon, mobile navigation template and accessibility
script are reused or adapted for the provider handbook. The upstream MIT
notice is preserved in
[the static asset license](../docs/_static/LICENSE-WsprryPi-Docs.txt).
No application source is included. Original independent documentation and
build configuration use MIT; the module and canonical UAPI licensing remain
unchanged.
The adapted scaffold is based on
[revision c0a0ec5](https://github.com/WsprryPi/WsprryPi-Docs/tree/c0a0ec5dd8ea6d7cb49fd7fa3d417ee0640c5672).

## Build configuration

Sphinx uses MyST Markdown, task lists and the shared image-delivery extension.
The extension supplies intrinsic image dimensions, asynchronous decoding and
eager loading for the first local content image. Later local images load lazily.
Explicit author sizing/loading is preserved, and print output retains its
builder's sizing defaults. Its regression fixture exercises clean and incremental
builds, nested sources, external images, explicit sizing and print output.

The direct Sphinx/MyST/theme versions are pinned in `docs/requirements.txt`,
alongside the scaffold's Requests and Pygments minimum versions. The handbook
uses no Python API autodocumentation, code introspection, developer TODOs or
editor language server, so those optional scaffold dependencies are unnecessary.

Version labels identify `main`, `devel` or a local checkout; `latest` displays
as `main`. The release label adds the checked-out Git revision. Hosted builds
use `READTHEDOCS_GIT_COMMIT_HASH` for that revision and
`READTHEDOCS_GIT_IDENTIFIER` for the source branch/tag. Pull request source links
use the exact commit rather than treating the pull request number as a branch.
These identifiers follow the
[Read the Docs environment-variable reference](https://docs.readthedocs.com/platform/stable/reference/environment-variables.html).

## Build locally

Use Python 3.14 and a disposable environment outside the checkout:

```sh
python3.14 -m venv /tmp/rp1-docs-venv
/tmp/rp1-docs-venv/bin/python -m pip install -r docs/requirements.txt
make docs DOCS_PYTHON=/tmp/rp1-docs-venv/bin/python \
  DOCS_BUILDDIR=/tmp/rp1-docs-build
make docs-check DOCS_PYTHON=/tmp/rp1-docs-venv/bin/python \
  DOCS_BUILDDIR=/tmp/rp1-docs-build
```

Open `/tmp/rp1-docs-build/html/index.html` for a preview. Check navigation, local
anchors and the mobile menu. Generated files stay outside the checkout.
`docs-check` runs the documentation regressions, strict HTML, EPUB, LaTeX source,
HTML Help, manual-page and Texinfo builds, and repository link/license/whitespace
checks. The Linux documentation CI job uses the same target and Python version
as Read the Docs. A separate Windows job checks the documentation regressions,
batch entry point and failed-build exit status. The ordinary module offline suite
does not require Sphinx. `sphinx -b linkcheck` can additionally check public
external URLs; network failures require interpretation rather than a blind URL rewrite.

The scaffold's platform entry points are kept with engineering tools:

- [Makefile](documentation/Makefile): `make -C engineering/documentation help`
  lists the Sphinx builders. Set `SPHINXBUILD` to the chosen environment's
  `python -m sphinx` command and `BUILDDIR` to an external output directory.
- [makedocs.sh](documentation/makedocs.sh): builds HTML without changing file
  ownership or deploying to a web server. Set `DOCS_PYTHON` and `BUILDDIR` as
  needed; extra arguments are passed to Sphinx.
- [make.bat](documentation/make.bat): after activating a Python 3.14 environment
  with the documentation dependencies, run
  `engineering\documentation\make.bat html` on Windows. It defaults to
  `%TEMP%\rp1-gpclk-dkms-docs` and preserves the Sphinx exit status.

The Makefile and shell helper default to a `rp1-gpclk-dkms-docs` directory under
`TMPDIR` or `/tmp`. These tools build documentation only. PDF compilation uses
the Read the Docs environment or an explicitly provisioned local TeX toolchain.
HTML Help, manual-page and Texinfo outputs are optional local exports; Read the
Docs publishes HTML, PDF, EPUB and the offline HTML archive.

## Read the Docs

The community project is **RP1-GPCLK-DKMS**, slug `rp1-gpclk-dkms`, sourced
from `https://github.com/WsprryPi/RP1-GPCLK-DKMS.git`. The root
[.readthedocs.yaml](../.readthedocs.yaml) selects `docs/conf.py`, Python 3.14,
pinned direct documentation dependencies and HTML/PDF/EPUB downloads.
Warnings fail the Sphinx build.

Maintain active **main** and **devel** branch versions. Set **main** as the
default published version and point the automatic `latest` alias at `main`.
Documentation branches do not replace tagged provider releases or modify
their assets or qualification scope.

The project's **Read the Docs Community GitHub App** integration receives
push webhooks and triggers builds for active versions. Its webhook is managed
by the GitHub App rather than a separate repository-hook entry. Keep that
integration connected to this repository.
After changing publication settings, verify both branch builds, their exact
commits and public pages. Test automatic triggering with a real documentation
push and inspect the integration's delivery/build result. Store no integration
token or webhook secret in this repository.

Project settings and builds are available from the
[community dashboard](https://app.readthedocs.org/projects/rp1-gpclk-dkms/).
The public branch URLs are
[main](https://rp1-gpclk-dkms.readthedocs.io/en/main/) and
[devel](https://rp1-gpclk-dkms.readthedocs.io/en/devel/).
