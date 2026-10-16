from docutils.parsers.rst import Parser as RstParser  # type: ignore
from sphinx.ext.napoleon.docstring import NumpyDocstring


class Parser(RstParser):
    """Parse NumPy-style docstrings as reStructuredText for autodoc2."""

    def parse(self, inputstring, document):
        napoleon_docstring = str(NumpyDocstring(inputstring))
        return super().parse(napoleon_docstring, document)
