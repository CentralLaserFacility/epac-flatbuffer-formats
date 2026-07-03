import numpy as np
from datetime import datetime
from epac.flatbuffers.arrays_wa00 import serialise_wa00
from epac.flatbuffers.pva0_data import serialise_data
from epac.flatbuffers import data_types as dt

np.random.seed(1234)
value = np.random.uniform(0.0, 1000.0, 10000)


def generate_wa00_dict():
    return {
        "values_x_array": value,
        "values_y_array": value,
        "timestamp": datetime(2025, 5, 7, 17, 55, 0, 410585),
        "x_timestamp": datetime(2025, 5, 7, 17, 35, 0, 410585),
        "y_unit": "some_units",
        "x_unit": "some_units",
    }


def generate_ntscalarany_dict():
    return {
        "value": value,
        "descriptor": "random nt scalar data",
        "alarm": {
            "severity": 2,
            "status": 1,
            "message": "NO_ALARM",
        },
        "timeStamp": {
            "secondsPastEpoch": 1746614207,
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


def generate_xydata_entry():
    ntscalarany_dict = generate_ntscalarany_dict()
    nt_scalar_obj = dt.NTScalarAny(**ntscalarany_dict)
    xydata_obj = dt.XYData(x=nt_scalar_obj, y=nt_scalar_obj)
    pv_data_obj = dt.PVData(data=xydata_obj, source_name="source name")
    return pv_data_obj


wa00_entry = generate_wa00_dict()
xydata_entry = generate_xydata_entry()


def test_wa00_benchmark(benchmark):
    benchmark(lambda: serialise_wa00(**wa00_entry))


def test_xydata_benchmark(benchmark):
    benchmark(lambda: serialise_data(xydata_entry))
