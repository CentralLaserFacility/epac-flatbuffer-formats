# Copied from https://github.com/ess-dmsc/python-streaming-data-types
# Upstream commit 3c2564cd6d

class StreamingDataTypesException(Exception):
    pass


class WrongSchemaException(StreamingDataTypesException):
    pass


class ShortBufferException(StreamingDataTypesException):
    pass
