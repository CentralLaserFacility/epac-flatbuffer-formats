# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from importlib.metadata import version as get_version

project = "EPAC Data Python Skeleton"
copyright = "2026, Central Laser Facility"
author = "Central Laser Facility"
release = get_version("epac-data-py-skeleton")
version = release

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: list = [
    "myst_parser",
    "autodoc2",
    "sphinx.ext.viewcode",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns: list = []

autodoc2_render_plugin = "myst"

autodoc2_packages = [
    {
        "path": "../../src/epac_data_py_skeleton",
        "module": "epac_data_py_skeleton",
    },
]

autodoc2_module_all_regexes: list = []

autodoc2_skip_module_regexes = [
    r".*\._.*",
]

autodoc2_output_dir = "_content/reference/api_docs"

autodoc2_hidden_objects = {"private"}

autodoc2_docstrings = "all"

myst_enable_extensions = ["colon_fence", "fieldlist"]

myst_substitutions = {
    "release": release,
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# PyData Theme has BSD 3-Clause License :
# only needs carrying forward if source code is used/modified

html_theme = "pydata_sphinx_theme"
html_title = "EPAC Data Python Skeleton"
html_theme_options: dict = {
    "github_url": "https://github.com/CentralLaserFacility/epac-data-py-skeleton",
    # logo
    "logo": {
        "link": "http://127.0.0.1:8000/",  # FIXME autobuild default serve
        "image_light": "_static/clf_logo_dark.png",
        "image_dark": "_static/clf_logo_light.png",
        "text": "EPAC Data Python Skeleton",
    },
    # Navbar (header)
    "navbar_align": "right",
    # Footer
    "footer_start": ["sphinx-version"],
    "footer_center": ["copyright"],
    "footer_end": ["theme-version"],
    # "announcement": "WE LOVE THE EPAC DATA TEAM",
}
html_static_path = ["_static"]
