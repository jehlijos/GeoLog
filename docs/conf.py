# -- Path setup --------------------------------------------------------------

import os
import sys

# cesta k src/ kvůli autodoc
sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------

project = "TOPAS"
author = "SZG"
release = "0.0.1"

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",            # Podpora Markdown vstupu
    "sphinx.ext.autodoc",     # Generování API z docstringů
    "sphinx.ext.napoleon",    # Google & NumPy style docstringy
    "sphinx.ext.autosummary", # Přehled modulů
]

autosummary_generate = True

# myst parser options (Markdown)
myst_enable_extensions = [
    "colon_fence",     # ::: blocks
    "deflist",         # definice
    "linkify",         # automatické URL
]

# If you want Markdown as source alongside .rst
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# -- Options for Markdown builder -------------------------------------------

# Pro sphinx-markdown-builder
markdown_builder_options = {
    "output_encoding": "utf-8",
}

# -- HTML / Markdown output --------------------------------------------------

# Ignorujeme složky, které nepotřebujeme generovat
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Autodoc settings --------------------------------------------------------

autoclass_content = "both"
autodoc_member_order = "groupwise"
autodoc_typehints = "description"

# -- Paths for templates ------------------------------------------------------

templates_path = ["_templates"]