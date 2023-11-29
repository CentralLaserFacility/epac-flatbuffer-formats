# Copied from https://github.com/ess-dmsc/python-streaming-data-types
# Upstream commit 3c2564cd6d

import pytest

from epac.flatbuffers.exceptions import ShortBufferException
from epac.flatbuffers.utils import check_schema_identifier


def test_schema_check_throws_if_buffer_too_short():
    short_buffer = b"1234567"
    with pytest.raises(ShortBufferException):
        check_schema_identifier(short_buffer, b"1234")
