from epac.flatbuffers.logdata_f142 import serialise_f142
from epac.flatbuffers.pva0_data import serialise_data
from epac.flatbuffers import data_types as dt


def generate_f142_dict():
    return {
        "source_name": "source_name",
        "value": 100,
        "timestamp_unix_ns": 1746612897685672960,
        "alarm_status": 3,
        "alarm_severity": 1,
        "units": "some_units",
    }


def generate_ntscalarany_dict():
    return {
        "value": 100,
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


def generate_ntscalarany_entry():
    ntscalarany_dict = generate_ntscalarany_dict()
    nt_scalar_obj = dt.NTScalarAny(**ntscalarany_dict)
    pv_data_obj = dt.PVData(data=nt_scalar_obj, source_name="source name")
    return pv_data_obj


f142_entry = generate_f142_dict()
ntscalarany_entry = generate_ntscalarany_entry()


def test_f142_benchmark(benchmark):
    benchmark(lambda: serialise_f142(**f142_entry))


def test_ntscalarany_benchmark(benchmark):
    benchmark(lambda: serialise_data(ntscalarany_entry))
