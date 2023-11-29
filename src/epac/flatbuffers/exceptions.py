# Copied from https://github.com/ess-dmsc/python-streaming-data-types
# Upstream commit 3c2564cd6d


class FlatbufferFormatException(Exception):
    pass


class WrongSchemaException(FlatbufferFormatException):
    pass


class ShortBufferException(FlatbufferFormatException):
    pass
