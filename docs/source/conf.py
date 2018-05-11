# -*- coding: utf-8 -*-

import os
import sys
import site

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../..'))

site.addsitedir(os.path.join(os.path.abspath(__file__), '../../'))

from luxon import metadata

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinxcontrib.napoleon',
]


# General information about the project.
project = metadata.description
copyright = metadata.copyright
author = metadata.author

version = metadata.version
release = version

# Sphinx
language = None
templates_path = ['_templates']
html_static_path = ['_static']
html_logo = '_static/img/logo.png'
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False

try:
    import tachyonic_sphinx
    html_theme = 'tachyonic'
    html_theme_path = tachyonic_sphinx.get_html_theme_path()
except ImportError:
    html_theme = 'default'

html_theme_options = {
}

htmlhelp_basename = metadata.project
