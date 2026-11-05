"""
Parser that converts Google-style docstrings to reStructuredText with
Sphinx Napoleon.
"""

from docutils.parsers.rst import Parser as RstParser
from sphinx.ext.napoleon.docstring import GoogleDocstring


class GoogleParser(RstParser):
    def parse(self, inputstring, document):
        # get the `Sphinx` configuration
        config = document.settings.env.config

        # convert docstrings to rst
        parsed_content = str(
            GoogleDocstring(
                inputstring,
                config,
            )
        )

        super().parse(parsed_content, document)


Parser = GoogleParser
