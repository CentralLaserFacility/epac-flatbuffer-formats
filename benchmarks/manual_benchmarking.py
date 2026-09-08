import argparse
import json
import time
import timeit
from pathlib import Path
from typing import Any, Callable

import numpy as np
from epac_flatbuffer_formats_rs import serialise_pv_data
from p4p.client.thread import Context  # type: ignore

from epac.flatbuffers.data_types import NTNDArray, NTScalarAny, NTTable, PVData, XYData
from epac.flatbuffers.pva0_data import serialise_data


def get_value(pv_name: str):
    cx = Context("pva", nt=False)
    got = cx.get(pv_name)
    return got


TYPE_MAP = {
    "epics:nt/NTNDArray:1.0": NTNDArray,
    "epics:nt/NTTable:1.0": NTTable,
    "epics:nt/NTScalar:1.0": NTScalarAny,
    "epics:nt/XYData:1.0": XYData,
}


def parse_to_pydantic(value, source_name):
    model = TYPE_MAP.get(value.getID())
    if model is None:
        raise ValueError(f"Unsupported type {value.getID()}")

    return PVData(
        data=model(**value.todict()),
        source_name=source_name,
        pulseId=None,
    )


def benchmark_pydantic_serialise(
    pv,
    serialiser: Callable,
    n: int = 10000,
    _print: bool = False,
) -> float:
    """
    Benchmark serialisation of a pydantic object using the supplied
    serialisation function.
    """
    value = get_value(pv)
    py_val = parse_to_pydantic(value, pv)

    result = timeit.timeit(
        lambda: serialiser(py_val),
        number=n,
    )

    if _print:
        print(f"{result / n * 1e6:.2f} µs per loop")

    return result / n


def benchmark_python_serialise(
    pv,
    n: int = 10000,
    _print: bool = False,
) -> float:
    return benchmark_pydantic_serialise(
        pv,
        serialise_data,
        n=n,
        _print=_print,
    )


def benchmark_rust_serialise(
    pv,
    n: int = 10000,
    _print: bool = False,
) -> float:
    return benchmark_pydantic_serialise(
        pv,
        serialise_pv_data,
        n=n,
        _print=_print,
    )


def collect_benchmark_stats(
    pv_list: list,
    n: int = 10_000,
    benchmark_repeats: int = 20,
    filename: str = "benchmark_data.json",
):
    """
    Collect and save benchmarking data to JSON.

    n:
        Number of serialisation calls per benchmark run.

    benchmark_repeats:
        Number of independent benchmark runs used to calculate
        mean and standard deviation.
    """

    data: dict[str, Any] = {
        "loop_repeats": n,
        "benchmark_repeats": benchmark_repeats,
        "results": {},
    }

    for pv in pv_list:
        pv_name = getattr(pv, "name", repr(pv))

        # ASCII progress bar
        def update_progress(i, total, label=""):
            width = 40
            filled = int(width * i / total)
            bar = "#" * filled + "-" * (width - filled)
            print(f"\r{label} [{bar}] {i}/{total}", end="", flush=True)

        rust_times = []
        print("Benchmarking rust...")
        for i in range(benchmark_repeats):
            val = benchmark_rust_serialise(pv, n) * 1e6
            rust_times.append(val)
            update_progress(i + 1, benchmark_repeats, "Rust")
        print()

        python_times = []
        print("Benchmarking python...")
        for i in range(benchmark_repeats):
            val = benchmark_python_serialise(pv, n) * 1e6
            python_times.append(val)
            update_progress(i + 1, benchmark_repeats, "Python")
        print()

        rust_mean = np.mean(rust_times)
        python_mean = np.mean(python_times)

        data["results"][pv_name] = {
            "rust": {
                "raw_micro": rust_times,
                "avg_micro": rust_mean,
                "std_dev_micro": np.std(rust_times),
            },
            "python": {
                "raw_micro": python_times,
                "avg_micro": python_mean,
                "std_dev_micro": np.std(python_times),
            },
            "speed_up": python_mean / rust_mean,
        }

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    annotate_stats(filename)


def annotate_stats(file_path: str) -> None:
    """
    Update benchmark JSON data in-place by adding:
      - speed_up = python avg_micro / rust avg_micro
      - var_coeff = std_dev_micro / avg_micro for both rust and python

    The JSON file is overwritten with the updated content.
    """

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data.get("results", {})

    for device_data in results.values():
        rust = device_data.setdefault("rust", {})
        python_data = device_data.setdefault("python", {})

        rust_avg = rust.get("avg_micro")
        py_avg = python_data.get("avg_micro")

        # Calculate speed_up if missing
        if "speed_up" not in device_data:
            if rust_avg and py_avg is not None:
                device_data["speed_up"] = py_avg / rust_avg

        # Calculate rust var_coeff if missing
        if "var_coeff" not in rust:
            rust_std = rust.get("std_dev_micro")
            if rust_avg not in (None, 0) and rust_std is not None:
                rust["var_coeff"] = rust_std / rust_avg

        # Calculate python var_coeff if missing
        if "var_coeff" not in python_data:
            py_std = python_data.get("std_dev_micro")
            if py_avg not in (None, 0) and py_std is not None:
                python_data["var_coeff"] = py_std / py_avg

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def print_folder_averages(folder_path: str) -> None:
    """
    Print average speed_up, rust var_coeff, and python var_coeff
    across all JSON benchmark files in the specified folder (and subtree).

    NOTE: this aggregates over devices so not always appropriate
    """

    speed_ups = []
    rust_var_coeffs = []
    python_var_coeffs = []

    file_count = 0
    device_count = 0

    for json_file in Path(folder_path).rglob("*.json"):
        file_count += 1

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for device_data in data.get("results", {}).values():
            device_count += 1

            if "speed_up" in device_data:
                speed_ups.append(device_data["speed_up"])

            rust = device_data.get("rust", {})
            if "var_coeff" in rust:
                rust_var_coeffs.append(rust["var_coeff"])

            python_data = device_data.get("python", {})
            if "var_coeff" in python_data:
                python_var_coeffs.append(python_data["var_coeff"])

    avg_speed_up = sum(speed_ups) / len(speed_ups) if speed_ups else float("nan")

    avg_rust_var_coeff = (
        sum(rust_var_coeffs) / len(rust_var_coeffs) if rust_var_coeffs else float("nan")
    )

    avg_python_var_coeff = (
        sum(python_var_coeffs) / len(python_var_coeffs)
        if python_var_coeffs
        else float("nan")
    )

    print(f"Files processed:           {file_count}")
    print(f"Devices processed:         {device_count}")
    print(f"Average speed-up:          {avg_speed_up:.3f}x")
    print(f"Average Rust var_coeff:    {avg_rust_var_coeff:.6f}")
    print(f"Average Python var_coeff:  {avg_python_var_coeff:.6f}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run benchmark collection against one or more PVs."
    )

    parser.add_argument(
        "pvs",
        nargs="+",
        help="PV names to benchmark",
    )

    parser.add_argument(
        "-n",
        "--samples",
        type=int,
        default=1000,
        help="Number of samples to collect (default: %(default)s)",
    )

    parser.add_argument(
        "-r",
        "--repeats",
        type=int,
        default=1,
        help="Number of benchmark repeats (default: %(default)s)",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="serialise_benchmark.json",
        help="Output filename",
    )

    args = parser.parse_args()

    start = time.time()

    print(f"Performing benchmarks for {len(args.pvs)} PVs...")

    collect_benchmark_stats(
        args.pvs,
        n=args.samples,
        benchmark_repeats=args.repeats,
        filename=args.output,
    )

    elapsed = time.time() - start
    print(f"Done. Time elapsed: {elapsed:.3f}s")


if __name__ == "__main__":
    main()
