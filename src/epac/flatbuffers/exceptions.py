"""Define exceptions raised while validating FlatBuffer format buffers.

The exception hierarchy distinguishes general format errors, unexpected
schema identifiers, and buffers that are too short to contain a header.
"""

# Copied from https://github.com/ess-dmsc/python-streaming-data-types
# Upstream commit 3c2564cd6d


class FlatbufferFormatException(Exception):
    """Base exception for errors in FlatBuffer format handling."""

    pass


class WrongSchemaException(FlatbufferFormatException):
    """Raised when a buffer contains an unexpected schema identifier."""

    pass


class ShortBufferException(FlatbufferFormatException):
    """Raised when a buffer is too short to contain the required header."""

    pass
