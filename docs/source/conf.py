
import sys
import os
import pkg_resources

# See what version of perkeeppy is installed to auto-detect our version.
# In a dev environment this requires that the repo be "installed" using
#   e.g. pip install -e .
detected_version = pkg_resources.get_distribution("perkeeppy").version

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
]

source_suffix = '.rst'
master_doc = 'index'

project = u'perkeeppy'
version = detected_version
release = detected_version

exclude_patterns = []

html_theme = 'alabaster'

intersphinx_mapping = {
    'http://docs.python.org/': None,
}
