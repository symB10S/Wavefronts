# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

import mock
 
MOCK_MODULES = ['numpy',  'matplotlib', 'matplotlib.pyplot']
for mod_name in MOCK_MODULES:
sys.modules[mod_name] = mock.Mock()

sys.path.insert(0, os.path.abspath('../..'))
# sys.path.insert(0, os.path.abspath('.'))

project = 'Wavefronts'
copyright = '2022, Jonathan Meerholz'
author = 'Jonathan Meerholz'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# import autodocsumm
extensions = [
    'sphinx.ext.autodoc',
    # "nbsphinx",
    # 'rst2pdf.pdfbuilder'
    # "autodocsumm"
    ]

pdf_documents = [('index', u'rst2pdf', u'Sample rst2pdf doc', u'Your Name'),]
pdf_stylesheets = ['twocolumn']

templates_path = ['_templates']
exclude_patterns = []
# autodoc_default_options = {"autosummary": True}



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
import sphinx_rtd_theme
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
