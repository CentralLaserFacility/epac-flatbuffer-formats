import numpy as np
import random
from datetime import datetime, timedelta
from epac.flatbuffers.area_detector_ADAr import serialise_ADAr, Attribute
from epac.flatbuffers.logdata_f142 import serialise_f142
from epac.flatbuffers.arrays_wa00 import serialise_wa00
from epac.flatbuffers.pva0_data import serialise_data
from epac.flatbuffers import data_types as dt


def generate_random_f142_entry():
    return (), {
        "source_name": f"source_{random.randint(0, 1000)}",
        "value": random.randint(0, 1000),
        "timestamp_unix_ns": int(datetime.now().timestamp() * 1e9),
        "alarm_status": random.choice([0, random.randint(1, 22)]),
        "alarm_severity": random.choice([0, random.randint(1, 4)]),
        "units": "some_units",
    }


def generate_random_adar_entry():
    return (), {
        "source_name": f"source_{random.randint(0, 1000)}",
        "unique_id": random.randint(0, 1000),
        "data": np.random.randint(0, 1000, size=(1000, 1000), dtype=np.uint64),
        "timestamp": datetime.now(),
        "attributes": [
            Attribute("name1", "desc1", "src1", "value"),
            Attribute("name2", "desc2", "src2", 11),
            Attribute("name3", "desc3", "src3", 3.14),
            Attribute("name4", "desc4", "src4", np.linspace(0, 10)),
        ],
    }


def generate_random_wa00_entry():
    size = 1000
    return (), {
        "values_x_array": np.random.uniform(0.0, 1000.0, size),
        "values_y_array": np.random.uniform(0.0, 1000.0, size),
        "timestamp": datetime.now(),
        "x_timestamp": datetime.now() - timedelta(minutes=random.randint(1, 60)),
        "y_unit": "some_units",
        "x_unit": "some_units",
    }


def generate_ntscalarany_dict():
    return {
        "value": random.randint(0, 1000),
        "descriptor": "random nt scalar data",
        "alarm": {
            "severity": random.choice([0, random.randint(1, 4)]),
            "status": random.choice([0, random.randint(1, 7)]),
            "message": "NO_ALARM",
        },
        "timeStamp": {
            "secondsPastEpoch": int(datetime.now().timestamp()),
            "nanoseconds": random.randint(0, 999999999),
            "userTag": 1,
        },
        "display": {
            "limitLow": 0,
            "limitHigh": 1000,
            "description": "some description",
            "units": "some_units",
            "precision": 2,
            "form": {
                "index": random.choice([0, random.randint(1, 6)]),
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


def generate_ntndarray_dict():
    return {
        "value": np.random.randint(0, 1000, size=300000, dtype=np.uint64),
        "descriptor": "random nt scalar data",
        "codec": {"name": ""},
        "compressedSize": 1000000,
        "uncompressedSize": 1000000,
        "dimension": [
            {
                "size": 1000,
                "offset": 0,
                "fullSize": 1000,
                "binning": 1,
                "reverse": False,
            },
            {
                "size": 1000,
                "offset": 0,
                "fullSize": 1000,
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
            "severity": random.choice([0, random.randint(1, 4)]),
            "status": random.choice([0, random.randint(1, 7)]),
            "message": "NO_ALARM",
        },
        "timeStamp": {
            "secondsPastEpoch": int(datetime.now().timestamp()),
            "nanoseconds": random.randint(0, 999999999),
            "userTag": 1,
        },
        "dataTimeStamp": {
            "secondsPastEpoch": int(datetime.now().timestamp()),
            "nanoseconds": random.randint(0, 999999999),
            "userTag": 1,
        },
        "display": {
            "limitLow": 0,
            "limitHigh": 1000,
            "description": "some description",
            "units": "some_units",
            "precision": 2,
            "form": {
                "index": random.choice([0, random.randint(1, 6)]),
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
    return (pv_data_obj,), {}


def generate_ntndarray_entry():
    ntndarray_dict = generate_ntndarray_dict()
    nt_array_obj = dt.NTNDArray(**ntndarray_dict)
    pv_data_obj = dt.PVData(data=nt_array_obj, source_name="source name")
    return (pv_data_obj,), {}


def test_f142_benchmark(benchmark):
    benchmark.pedantic(serialise_f142, setup=generate_random_f142_entry, rounds=10000)


def test_f142_benchmark_2(benchmark):
    random.seed(1234)
    entries = [generate_random_f142_entry()[1] for _ in range(100)]
    import itertools

    entries = itertools.cycle(entries)
    benchmark(lambda: serialise_f142(**next(entries)))


def test_f142_benchmark_3(benchmark):
    random.seed(1234)
    entries = [generate_random_f142_entry()[1] for _ in range(100)]
    import itertools

    entries = itertools.cycle(entries)

    def dummy(**kwargs):
        pass

    benchmark(lambda: dummy(**next(entries)))


def test_adar_benchmark(benchmark):
    benchmark.pedantic(serialise_ADAr, setup=generate_random_adar_entry, rounds=10000)


def test_wa00_benchmark(benchmark):
    benchmark.pedantic(serialise_wa00, setup=generate_random_wa00_entry, rounds=10000)


def test_ntscalarany_benchmark(benchmark):
    benchmark.pedantic(serialise_data, setup=generate_ntscalarany_entry, rounds=10000)


def test_ntndarray_benchmark(benchmark):
    random.seed(1234)
    benchmark.pedantic(serialise_data, setup=generate_ntndarray_entry, rounds=2500)


def test_ntndarray_benchmark_2(benchmark):
    random.seed(1234)
    entries = [generate_ntndarray_entry()[0][0] for _ in range(2)]
    import itertools

    entries = itertools.cycle(entries)
    entry = next(entries)
    benchmark.pedantic(lambda: serialise_data(entry), rounds=2500)


def test_ntndarray_benchmark_3(benchmark):
    random.seed(1234)
    entries = [generate_ntndarray_entry()[0][0] for _ in range(2)]
    import itertools

    entries = itertools.cycle(entries)
    entry = next(entries)

    def foo():
        serialise_data(entry)

    benchmark.pedantic(foo, rounds=2500)
