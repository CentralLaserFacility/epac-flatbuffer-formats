import numpy as np
import random
from datetime import datetime, timedelta
from epac.flatbuffers.area_detector_ADAr import serialise_ADAr, Attribute
from epac.flatbuffers.logdata_f142 import serialise_f142
from epac.flatbuffers.arrays_wa00 import serialise_wa00
from epac.flatbuffers.pva0_data import serialise_data
from epac.flatbuffers import data_types as dt
import time
import gc
from typing import Callable, Any


def generate_random_f142_entry():
    return {
        "source_name": f"source_{random.randint(0, 1000)}",
        "value": random.randint(0, 1000),
        "timestamp_unix_ns": int(datetime.now().timestamp() * 1e9),
        "alarm_status": random.choice([0, random.randint(1, 22)]),
        "alarm_severity": random.choice([0, random.randint(1, 4)]),
        "units": "some_units",
    }


def generate_random_adar_entry():
    return {
        "source_name": f"source_{random.randint(0, 1000)}",
        "unique_id": random.randint(0, 1000),
        "data": np.random.randint(0, 1000, size=(1, 1000000), dtype=np.uint64),
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
    return {
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
        "value": np.random.randint(0, 1000, size=1000000, dtype=np.uint64),
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
    return {"data": pv_data_obj}


def generate_ntndarray_entry():
    ntndarray_dict = generate_ntndarray_dict()
    nt_array_obj = dt.NTNDArray(**ntndarray_dict)
    pv_data_obj = dt.PVData(data=nt_array_obj, source_name="source name")
    return {"data": pv_data_obj}


def simple_benchmark(
    setup_fn: Callable[[], Any], benchmark_fn: Callable[[Any], None], count: int = 1000
):
    """
    Benchmark a function over multiple iterations using high-resolution timer.

    Args:
        setup_fn (Callable[[], Any]): Function to generate input data for each iteration.
        benchmark_fn (Callable[[Any], None]): Function to benchmark, called with the result of setup_fn.
        count (int): Number of iterations.
    """
    gc_was_enabled = gc.isenabled()
    gc.disable()  # disable GC for consistency
    random.seed(1234)  # fix the random seed

    times_ns = np.empty(count, dtype=np.int64)
    entries = []

    for i in range(count):
        entry = setup_fn()
        entries.append(entry)

    for i in range(count):
        start = time.perf_counter_ns()
        benchmark_fn(**entry)
        times_ns[i] = time.perf_counter_ns() - start

    if gc_was_enabled:
        gc.enable()

    print(f"Benchmark results over {count} runs for {setup_fn.__name__}:")
    print(f"Mean:   {np.mean(times_ns) / 1e6:.3f} ms")
    print(f"Median: {np.median(times_ns) / 1e6:.3f} ms")
    print(f"Min:    {np.min(times_ns) / 1e6:.3f} ms")
    print(f"Max:    {np.max(times_ns) / 1e6:.3f} ms")


if __name__ == "__main__":
    simple_benchmark(
        setup_fn=generate_random_f142_entry, benchmark_fn=serialise_f142, count=1000
    )
    simple_benchmark(
        setup_fn=generate_random_adar_entry, benchmark_fn=serialise_ADAr, count=100
    )
    simple_benchmark(
        setup_fn=generate_random_wa00_entry, benchmark_fn=serialise_wa00, count=1000
    )
    simple_benchmark(
        setup_fn=generate_ntscalarany_entry, benchmark_fn=serialise_data, count=1000
    )
    simple_benchmark(
        setup_fn=generate_ntndarray_entry, benchmark_fn=serialise_data, count=100
    )
