import numpy as np
import pytest
from datetime import datetime, timezone, timedelta
from epac.flatbuffers import DESERIALISERS, SERIALISERS
from epac.flatbuffers.arrays_wa00 import (
    deserialise_wa00,
    serialise_wa00,
)
from epac.flatbuffers.exceptions import WrongSchemaException


class TestSerialisationwa00:
    def test_serialise_and_deserialise_wa00_int_array(self):
        """
        Round-trip to check that we serialise is what we get back.
        """
        original_entry = {
            "values_x_array": np.array([1, 2, 3, 4, 5, 1], dtype=np.uint64),
            "values_y_array": np.array([6, 7, 8, 9, 10, 6], dtype=np.uint64),
            "timestamp": datetime.now(tz=timezone.utc),
            "x_timestamp": datetime.now(tz=timezone.utc) - timedelta(minutes=5),
            "y_unit": "vs",
            "x_unit": "ss",
        }

        buf = serialise_wa00(**original_entry)
        entry = deserialise_wa00(buf)
        assert entry.timestamp == original_entry["timestamp"]
        assert entry.x_timestamp == original_entry["x_timestamp"]
        assert entry.y_unit == original_entry["y_unit"]
        assert entry.x_unit == original_entry["x_unit"]
        assert np.array_equal(entry.values_x_array, original_entry["values_x_array"])
        assert np.array_equal(entry.values_y_array, original_entry["values_y_array"])

    def test_serialise_and_deserialise_wa00_int_array_without_option(self):
        original_entry_without_option = {
            "values_x_array": np.array([1, 2, 3, 4, 5, 1], dtype=np.uint64),
            "values_y_array": np.array([6, 7, 8, 9, 10, 6], dtype=np.uint64),
        }

        buf = serialise_wa00(**original_entry_without_option)
        entry = deserialise_wa00(buf)
        assert entry.timestamp is None
        assert entry.x_timestamp is None
        assert entry.y_unit is None
        assert entry.x_unit is None
        assert np.array_equal(
            entry.values_x_array, original_entry_without_option["values_x_array"]
        )
        assert np.array_equal(
            entry.values_y_array, original_entry_without_option["values_y_array"]
        )

    def test_if_buffer_has_wrong_id_then_throws(self):
        original_entry = {
            "values_x_array": np.array([1, 2, 3, 4, 5, 1], dtype=np.uint64),
            "values_y_array": np.array([6, 7, 8, 9, 10, 6], dtype=np.uint64),
            "timestamp": datetime.now(tz=timezone.utc),
            "x_timestamp": datetime.now(tz=timezone.utc) - timedelta(minutes=5),
            "y_unit": "vs",
            "x_unit": "ss",
        }

        buf = serialise_wa00(**original_entry)

        # Manually hack the id
        buf = bytearray(buf)
        buf[4:8] = b"1234"

        with pytest.raises(WrongSchemaException):
            deserialise_wa00(buf)

    def test_schema_type_is_in_global_serialisers_list(self):
        assert "wa00" in SERIALISERS
        assert "wa00" in DESERIALISERS
