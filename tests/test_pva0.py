import pytest
import numpy as np

from epac.flatbuffers import data_types as dt
from epac.flatbuffers.pva0_data import (
    deserialise_data,
    serialise_data,
)


class TestSerialisationPVA0:
    source_name = "test-pv"
    pulseid = {"value": 1739946490, "timestamp": 1739946490.410324754}

    @pytest.fixture
    def nt_scalar_dict(self):
        return {
            "value": 1,
            "descriptor": "test nt scalar data",
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

    @pytest.fixture
    def nt_ndarray_dict(self):
        return {
            "value": np.array([91, 92, 93, 102, 103, 104], dtype=np.uint8),
            "codec": {"name": ""},
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
                    "alarm": None,
                    "time": None,
                    "tags": ["tag1", "tag2"],
                },
                {
                    "name": "Empty",
                    "value": None,
                    "descriptor": "",
                    "sourceType": 0,
                    "source": "",
                    "alarm": None,
                    "time": None,
                    "tags": [],
                },
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
                "units": "pixels",
                "precision": 1,
            },
        }

    def test_ntscalarany_pydantic_correctly_captures_information(self, nt_scalar_dict):
        nt_scalar_obj = dt.NTScalarAny(**nt_scalar_dict)
        assert {k: v for k, v in nt_scalar_dict.items() if k != "display"} == {
            k: v for k, v in nt_scalar_obj.model_dump().items() if k != "display"
        }
        assert {k: v for k, v in nt_scalar_dict["display"].items() if k != "form"} == {
            k: v
            for k, v in nt_scalar_obj.model_dump()["display"].items()
            if k != "form"
        }
        assert nt_scalar_obj.model_dump()["display"]["form"] == 0

    def test_ntndarray_pydantic_correctly_captures_information(self, nt_ndarray_dict):
        nt_ndarray_obj = dt.NTNDArray(**nt_ndarray_dict)
        assert {
            k: v for k, v in nt_ndarray_dict.items() if k not in {"display", "value"}
        } == {
            k: v
            for k, v in nt_ndarray_obj.model_dump().items()
            if k not in {"display", "value"}
        }
        assert {k: v for k, v in nt_ndarray_dict["display"].items() if k != "form"} == {
            k: v
            for k, v in nt_ndarray_obj.model_dump()["display"].items()
            if k != "form"
        }
        assert nt_ndarray_obj.model_dump()["display"]["form"] == 0
        assert np.array_equal(nt_ndarray_dict["value"], nt_ndarray_obj.value)

    def test_serialises_and_deserialises_xydata_correctly(self, nt_scalar_dict):

        nt_scalar_obj = dt.NTScalarAny(**nt_scalar_dict)
        xydata_obj = dt.XYData(x=nt_scalar_obj, y=nt_scalar_obj)
        pulseid_obj = dt.PulseID(
            value=self.pulseid["value"], timestamp=self.pulseid["timestamp"]
        )
        pv_data_obj = dt.PVData(
            data=xydata_obj,
            sourceName=self.source_name,
            pulseId=pulseid_obj,
            modifiedTimeStamp=nt_scalar_obj.timeStamp,
        )
        buf = serialise_data(pv_data_obj)
        assert isinstance(buf, bytes)
        deserialised_obj = deserialise_data(buf)
        assert deserialised_obj == pv_data_obj

    def test_serialises_and_deserialises_scalar_ntscalarany_correctly(
        self, nt_scalar_dict
    ):

        nt_scalar_obj = dt.NTScalarAny(**nt_scalar_dict)
        pulseid_obj = dt.PulseID(
            value=self.pulseid["value"], timestamp=self.pulseid["timestamp"]
        )
        pv_data_obj = dt.PVData(
            data=nt_scalar_obj,
            sourceName=self.source_name,
            pulseId=pulseid_obj,
            modifiedTimeStamp=nt_scalar_obj.timeStamp,
        )
        buf = serialise_data(pv_data_obj)
        assert isinstance(buf, bytes)
        deserialised_obj = deserialise_data(buf)
        assert deserialised_obj == pv_data_obj

    def test_serialises_and_deserialises_ntndarray_correctly(self, nt_ndarray_dict):

        nt_ndarray_obj = dt.NTNDArray(**nt_ndarray_dict)
        pulseid_obj = dt.PulseID(
            value=self.pulseid["value"], timestamp=self.pulseid["timestamp"]
        )
        pv_data_obj = dt.PVData(
            data=nt_ndarray_obj,
            sourceName=self.source_name,
            pulseId=pulseid_obj,
            modifiedTimeStamp=nt_ndarray_obj.timeStamp,
        )
        buf = serialise_data(pv_data_obj)
        assert isinstance(buf, bytes)
        deserialised_obj = deserialise_data(buf)
        assert np.array_equal(deserialised_obj.data.value, pv_data_obj.data.value)
        deserialised_obj.data.value = None
        pv_data_obj.data.value = None
        assert deserialised_obj == pv_data_obj

    def test_raises_error_on_missing_value(self):
        nt_scalar_dict = {
            "value": None,
        }

        nt_ndarray_dict = {
            "value": None,
        }

        nt_column_dict = {
            "value": None,
        }

        ca_scalar_dict = {
            "value": None,
        }

        with pytest.raises(ValueError):
            dt.NTScalarAny(**nt_scalar_dict)

        with pytest.raises(ValueError):
            dt.NTNDArray(**nt_ndarray_dict)

        with pytest.raises(ValueError):
            dt.Column(**nt_column_dict)

        with pytest.raises(ValueError):
            dt.CAScalarAny(**ca_scalar_dict)

    def test_serialises_and_deserialises_missing_ntscalarany_fields_correctly(self):
        nt_scalar_dict = {
            "value": 1,
        }

        nt_scalar_obj = dt.NTScalarAny(**nt_scalar_dict)
        pv_data_obj = dt.PVData(data=nt_scalar_obj, sourceName=self.source_name)
        buf = serialise_data(pv_data_obj)
        deserialised_obj = deserialise_data(buf)
        assert deserialised_obj == pv_data_obj

    def test_serialises_and_deserialises_missing_ntndarray_fields_correctly(self):
        nt_ndarray_dict = {
            "value": np.array([91, 92, 93, 102, 103, 104], dtype=np.uint8),
        }

        nt_ndarray_obj = dt.NTNDArray(**nt_ndarray_dict)
        pv_data_obj = dt.PVData(data=nt_ndarray_obj, sourceName=self.source_name)
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
            1.23,  # float
            [1.23, 4.56, 7.89],  # float array
        ],
    )
    def test_serialises_and_deserialises_any_values_correctly(self, value):
        nt_scalar_dict = {
            "value": value,
        }

        nt_scalar_obj = dt.NTScalarAny(**nt_scalar_dict)
        pulseid_obj = dt.PulseID(
            value=self.pulseid["value"], timestamp=self.pulseid["timestamp"]
        )
        pv_data_obj = dt.PVData(
            data=nt_scalar_obj,
            sourceName=self.source_name,
            pulseId=pulseid_obj,
        )
        buf = serialise_data(pv_data_obj)
        deserialised_obj = deserialise_data(buf)
        assert np.array_equal(deserialised_obj.data.value, pv_data_obj.data.value)
