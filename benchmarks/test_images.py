import numpy as np
import pytest
from datetime import datetime
from epac.flatbuffers.area_detector_ADAr import serialise_ADAr, Attribute
from epac.flatbuffers.pva0_data import serialise_data
from epac.flatbuffers import data_types as dt


def generate_adar_dict(size):
    np.random.seed(1234)
    return {
        "source_name": "source_name",
        "unique_id": 100,
        "data": np.random.randint(0, 1000, size=(size, size), dtype=np.uint16),
        "timestamp": datetime(2025, 5, 7, 17, 55, 0, 410585),
        "attributes": [
            Attribute("name1", "desc1", "src1", "value"),
            Attribute("name2", "desc2", "src2", 11),
            Attribute("name3", "desc3", "src3", 3.14),
            Attribute("name4", "desc4", "src4", np.linspace(0, 10)),
        ],
    }


def generate_ntndarray_dict(size):
    np.random.seed(1234)
    return {
        "value": np.random.randint(0, 1000, size=size**2, dtype=np.uint16),
        "descriptor": "random nt scalar data",
        "codec": {"name": ""},
        "compressedSize": size**2,
        "uncompressedSize": size**2,
        "dimension": [
            {
                "size": size,
                "offset": 0,
                "fullSize": size,
                "binning": 1,
                "reverse": False,
            },
            {
                "size": size,
                "offset": 0,
                "fullSize": size,
                "binning": 1,
                "reverse": False,
            },
        ],
        "uniqueId": 16991836,
        "attribute": [
            {
                "name": "nam1",
                "value": "value",
                "descriptor": "Color mode",
                "sourceType": 0,
                "source": "Driver",
                "alarm": None,
                "time": None,
                "tags": ["tag1", "tag2"],
            },
            {
                "name": "name2",
                "value": 11,
                "descriptor": "Color mode",
                "sourceType": 0,
                "source": "Driver",
                "alarm": None,
                "time": None,
                "tags": ["tag1", "tag2"],
            },
            {
                "name": "name3",
                "value": 3.14,
                "descriptor": "Color mode",
                "sourceType": 0,
                "source": "Driver",
                "alarm": None,
                "time": None,
                "tags": ["tag1", "tag2"],
            },
            {
                "name": "name4",
                "value": np.linspace(0, 10),
                "descriptor": "Color mode",
                "sourceType": 0,
                "source": "Driver",
                "alarm": None,
                "time": None,
                "tags": ["tag1", "tag2"],
            },
        ],
        "alarm": {
            "severity": 2,
            "status": 1,
            "message": "HIGH",
        },
        "timeStamp": {
            "secondsPastEpoch": 1746620864,
            "nanoseconds": 999999999,
            "userTag": 1,
        },
        "dataTimeStamp": {
            "secondsPastEpoch": 1746620864,
            "nanoseconds": 999999999,
            "userTag": 1,
        },
        "display": {
            "limitLow": 0,
            "limitHigh": 1000,
            "description": "some description",
            "units": "some_units",
            "precision": 2,
            "form": {
                "index": 3,
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
        "control": {
            "limitLow": 0,
            "limitHigh": 1000,
            "minStep": 1,
        },
    }


def generate_ntndarray_entry(size):
    ntndarray_dict = generate_ntndarray_dict(size)
    nt_array_obj = dt.NTNDArray(**ntndarray_dict)
    pv_data_obj = dt.PVData(data=nt_array_obj, source_name="source name")
    return pv_data_obj


# A range of image sizes is chosen as this significantly impacts performance


@pytest.mark.parametrize("size", [10, 30, 100, 300, 1000])
def test_adar_benchmark(benchmark, size):
    adar_entry = generate_adar_dict(size)
    benchmark(lambda: serialise_ADAr(**adar_entry))


@pytest.mark.parametrize("size", [10, 30, 100, 300, 1000])
def test_ntndarray_benchmark(benchmark, size):
    ntndarray_entry = generate_ntndarray_entry(size)
    benchmark(lambda: serialise_data(ntndarray_entry))
