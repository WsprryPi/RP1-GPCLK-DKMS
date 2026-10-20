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

## Build locally

Use Python 3.14 and a disposable environment outside the checkout:

```sh
python3.14 -m venv /tmp/rp1-docs-venv
/tmp/rp1-docs-venv/bin/python -m pip install -r docs/requirements.txt
/tmp/rp1-docs-venv/bin/python -m sphinx -n -W --keep-going \
  -b html docs /tmp/rp1-docs-html
/tmp/rp1-docs-venv/bin/python -m sphinx -n -W --keep-going \
  -b epub docs /tmp/rp1-docs-epub
python3 tests/check_doc_links.py
python3 tests/check_spdx.py
git diff --check
```

Open `/tmp/rp1-docs-html/index.html` for a preview. Check navigation, local
anchors and the mobile menu. Generated files stay outside the checkout.
The documentation CI job performs strict HTML and EPUB builds and repository
link/license checks. `sphinx -b linkcheck` can additionally check public external
URLs; network failures require interpretation rather than a blind URL rewrite.

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

The project's GitHub integration receives push webhooks and triggers builds
for active versions. Keep that integration connected to this repository.
After changing publication settings, verify both branch builds, their exact
commits and public pages. Test automatic triggering with a real documentation
push and inspect the integration's delivery/build result. Store no integration
token or webhook secret in this repository.

Project settings and builds are available from the
[community dashboard](https://app.readthedocs.org/projects/rp1-gpclk-dkms/).
The public branch URLs are
[main](https://rp1-gpclk-dkms.readthedocs.io/en/main/) and
[devel](https://rp1-gpclk-dkms.readthedocs.io/en/devel/).
