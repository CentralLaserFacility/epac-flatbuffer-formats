import pytest
import numpy as np

from epac.flatbuffers import data_types as dt
from epac.flatbuffers.pva0_data import (
    deserialise_data,
    serialise_data,
)


class TestSerialisationPVA0:
    pv_name = "test-pv"

    def test_serialises_and_deserialises_scalar_ntscalarany_correctly(self):
        nt_scalar_dict = {
            "value": 1,
            "alarm": {"severity": 0, "status": 0, "message": "NO_ALARM"},
            "timeStamp": {
                "secondsPastEpoch": 1739946490,
                "nanoseconds": 410324754,
                "userTag": 0,
            },
            "display": {
                "limitLow": 0.0,
                "limitHigh": 0.0,
                "description": "Application Directory",
                "units": "u",
                "precision": 0,
                "form": {
                    "index": 0,
                    "choices": [
                        "Default",
                        "String",
                        "Binary",
                        "Decimal",
                        "Hex",
                        "Exponential",
                        "Engineering",
                    ],
                },
            },
            "control": {"limitLow": 0.0, "limitHigh": 0.0, "minStep": 0.0},
        }

        nt_scalar_obj = dt.NTScalarAny(**nt_scalar_dict)
        pv_data_obj = dt.PVData(data=nt_scalar_obj, pv_name=self.pv_name)
        buf = serialise_data(pv_data_obj)
        deserialised_obj = deserialise_data(buf)
        assert deserialised_obj == pv_data_obj

    def test_serialises_and_deserialises_ntndarray_correctly(self):
        nt_ndarray_dict = {
            "value": np.array([91, 92, 93, 102, 103, 104], dtype=np.uint8),
            "codec": {"name": "", "parameters": 5},
            "compressedSize": 6,
            "uncompressedSize": 6,
            "dimension": [
                {"size": 1, "offset": 0, "fullSize": 1, "binning": 1, "reverse": False},
                {"size": 6, "offset": 0, "fullSize": 6, "binning": 1, "reverse": False},
            ],
            "uniqueId": 16991836,
            "dataTimeStamp": {
                "secondsPastEpoch": 1740045680,
                "nanoseconds": 233594894,
                "userTag": 0,
            },
            "attribute": [
                {
                    "name": "ColorMode",
                    "value": 0,
                    "descriptor": "Color mode",
                    "sourceType": 0,
                    "source": "Driver",
                }
            ],
            "descriptor": "",
            "alarm": {"severity": 0, "status": 0, "message": "NO_ALARM"},
            "timeStamp": {
                "secondsPastEpoch": 1740045680,
                "nanoseconds": 233594955,
                "userTag": 0,
            },
            "display": {
                "limitLow": 0.0,
                "limitHigh": 0.0,
                "description": "Example NDArray",
                "format": "",
                "units": "pixels",
            },
        }

        nt_ndarray_obj = dt.NTNDArray(**nt_ndarray_dict)
        pv_data_obj = dt.PVData(data=nt_ndarray_obj, pv_name=self.pv_name)
        buf = serialise_data(pv_data_obj)
        deserialised_obj = deserialise_data(buf)
        assert np.array_equal(deserialised_obj.data.value, pv_data_obj.data.value)
        deserialised_obj.data.value = None
        pv_data_obj.data.value = None
        assert deserialised_obj == pv_data_obj

    def test_raises_error_on_missing_value(self):
        nt_scalar_dict = {
            "value": None,
        }

        nt_scalar_obj = dt.NTScalarAny(**nt_scalar_dict)
        pv_data_obj = dt.PVData(data=nt_scalar_obj, pv_name=self.pv_name)
        with pytest.raises(ValueError):
            serialise_data(pv_data_obj)

    def test_serialises_and_deserialises_missing_ntscalarany_fields_correctly(self):
        nt_scalar_dict = {
            "value": 1,
        }

        nt_scalar_obj = dt.NTScalarAny(**nt_scalar_dict)
        pv_data_obj = dt.PVData(data=nt_scalar_obj, pv_name=self.pv_name)
        buf = serialise_data(pv_data_obj)
        deserialised_obj = deserialise_data(buf)
        assert deserialised_obj == pv_data_obj

    def test_serialises_and_deserialises_missing_ntndarray_fields_correctly(self):
        nt_ndarray_dict = {
            "value": np.array([91, 92, 93, 102, 103, 104], dtype=np.uint8),
        }

        nt_ndarray_obj = dt.NTNDArray(**nt_ndarray_dict)
        pv_data_obj = dt.PVData(data=nt_ndarray_obj, pv_name=self.pv_name)
        buf = serialise_data(pv_data_obj)
        deserialised_obj = deserialise_data(buf)
        assert np.array_equal(deserialised_obj.data.value, pv_data_obj.data.value)
        deserialised_obj.data.value = None
        pv_data_obj.data.value = None
        assert deserialised_obj == pv_data_obj

    @pytest.mark.parametrize(
        "value",
        [
            "test",  # string
            ["test1", "test2", "test3"],  # string array
            1,  # int
            [1, 2, 3],  # int array
            0x7F,  # byte
            [0x7E, 0x7F, 0xFF],  # byte array
            1.23,  # float
            [1.23, 4.56, 7.89],  # float array
        ],
    )
    def test_serialises_and_deserialises_any_values_correctly(self, value):
        nt_scalar_dict = {
            "value": value,
        }

        nt_scalar_obj = dt.NTScalarAny(**nt_scalar_dict)
        pv_data_obj = dt.PVData(data=nt_scalar_obj, pv_name=self.pv_name)
        buf = serialise_data(pv_data_obj)
        deserialised_obj = deserialise_data(buf)
        assert np.array_equal(deserialised_obj.data.value, pv_data_obj.data.value)
