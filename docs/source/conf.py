# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from importlib.metadata import version as get_version
from pathlib import Path

conf_dir = str(Path(__file__).parent)
if conf_dir not in sys.path:
    sys.path.insert(0, conf_dir)

# ---------------------------------------------------------------------------
# Project information
# ---------------------------------------------------------------------------
project = "EPAC Flatbuffer Formats"
copyright = "2026, Central Laser Facility"
author = "Central Laser Facility"
release = get_version("epac-flatbuffer-formats")
version = release

# ---------------------------------------------------------------------------
# General configuration
# ---------------------------------------------------------------------------
extensions: list = [
    "myst_parser",
    "autodoc2",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns: list = []

# ---------------------------------------------------------------------------
# autodoc2 configuration
# ---------------------------------------------------------------------------
autodoc2_render_plugin = "myst"
autodoc2_docstrings = "direct"

autodoc2_docstring_parser_regexes = [
    (r".*", "utils"),
]
autodoc2_hidden_objects = {"private", "inherited"}
autodoc2_module_summary = True
autodoc2_sort_names = True
autodoc2_annotations = True
autodoc2_class_inheritance = True
autodoc2_class_docstring = "merge"
autodoc2_typehints = "signature"
autodoc2_member_order = "groupwise"
autodoc2_output_dir = "_content/reference/api_docs"
autodoc2_module_all_regexes: list = []
autodoc2_skip_module_regexes = [r".*\._.*"]

autodoc_default_options = {
    "inherited-members": False,
}

autodoc2_packages = [
    {
        "path": "../../src/epac/flatbuffers",
        "module": "epac.flatbuffers",
        "exclude_dirs": ["fbschemas"],
    },
    {
        "path": "../../rust/epac-flatbuffer-formats-rs/python/epac_flatbuffer_formats_rs/_bindings.pyi",
        "module": "epac_flatbuffer_formats_rs",
    },
    {"path": "../../dev.py", "module": "dev.py"},
]

# ---------------------------------------------------------------------------
# Docstring and cross-reference configuration
# ---------------------------------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://pydantic.dev/docs/validation/latest/", None),
}

# use regex to select parser (currenlt all use google parser)
autodoc2_docstring_parser_regexes = [
    (
        r".*",
        "utils",
    ),
]

# Suppress duplicate item warnings for generated API docs.
suppress_warnings = ["autodoc2.dup_item"]

# MyST configuration for rendered API markdown.
myst_enable_extensions = ["colon_fence", "fieldlist"]
myst_substitutions = {"release": release}

autosummary_generate = True

# ---------------------------------------------------------------------------
# HTML output
# ---------------------------------------------------------------------------
html_theme = "pydata_sphinx_theme"
html_title = "EPAC Flatbuffer Formats"
html_theme_options: dict = {
    "github_url": "https://github.com/CentralLaserFacility/epac-flatbuffer-formats",
    "logo": {
        "link": "http://127.0.0.1:8000/",  # FIXME: autobuild default serve
        "image_light": "_static/stfc_logo_dark.png",
        "image_dark": "_static/stfc_logo_light.png",
        "text": "EPAC Flatbuffer Formats",
    },
    "navbar_align": "right",
    "footer_start": ["sphinx-version"],
    "footer_center": ["copyright"],
    "footer_end": ["theme-version"],
    # "announcement": "WE LOVE THE EPAC DATA TEAM",
}
html_css_files = ["navbar_shift.css"]
html_static_path = ["_static"]
