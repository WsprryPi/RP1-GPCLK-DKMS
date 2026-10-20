# SPDX-License-Identifier: MIT
"""Operator handbook, adapted from the MIT-licensed WsprryPi-Docs scaffold."""

import os
from pathlib import Path
import subprocess

project = "RP1 GPCLK DKMS"
author = "Lee C. Bussy"
copyright = "2026, Lee Bussy; scaffold copyright 2024 Lee Bussy"

try:
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=Path(__file__).parent,
        stderr=subprocess.DEVNULL, text=True,
    ).strip()
except (OSError, subprocess.CalledProcessError):
    branch = "local"

version = os.environ.get("READTHEDOCS_VERSION_NAME", branch) or "local"
if version == "latest":
    version = "main"
release = version

extensions = ["myst_parser"]
source_suffix = {".md": "markdown"}
root_doc = "index"
language = "en"
exclude_patterns = ["_build", ".venv", "Thumbs.db", ".DS_Store"]
myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3
nitpicky = True

html_theme = "sphinx_rtd_theme"
html_title = "RP1 GPCLK DKMS operator handbook"
html_theme_options = {
    "logo_only": False,
    "prev_next_buttons_location": "both",
    "style_external_links": True,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 3,
    "includehidden": True,
    "titles_only": True,
}
templates_path = ["_templates"]
html_static_path = ["_static"]
html_logo = "_static/WsprryPi_Logo.png"
html_favicon = "_static/favicon.ico"
html_css_files = ["css/custom.css"]
html_js_files = ["js/accessibility.js"]
html_context = {
    "display_github": True,
    "github_user": "WsprryPi",
    "github_repo": "RP1-GPCLK-DKMS",
    "github_version": os.environ.get("READTHEDOCS_GIT_IDENTIFIER", branch),
    "conf_py_path": "/docs/",
}

latex_documents = [
    ("index", "RP1-GPCLK-DKMS.tex", "RP1 GPCLK DKMS Operator Handbook",
     author, "manual"),
]
epub_title = html_title
epub_exclude_files = ["search.html", "_static/LICENSE-WsprryPi-Docs.txt"]

# Local static assets used by the HTML theme are not EPUB reading content.
suppress_warnings = ["epub.unknown_project_files"]
