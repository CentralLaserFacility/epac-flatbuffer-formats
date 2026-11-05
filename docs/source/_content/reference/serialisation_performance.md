# `pva0` Serialisation Performance

## Benchmark Methodology

Benchmarks were performed using 20 repeats with 10,000 samples per repeat. Reported speedups include both:

1. Conversion of the source Python/Pydantic object into the Rust representation.
2. Serialisation of the resulting Rust object.

Speedups are measured relative to the Python serialisation implementation.

```{note}
The benchmarking code used to compare serialisation implementations is pushed to the repository:
[`benchmarks/manual_benchmarking.py`](https://github.com/CentralLaserFacility/epac-flatbuffer-formats/blob/development/benchmarks/manual_benchmarking.py).
```

## Results

| System | Data Type | Size | Speedup |
|----------|----------|----------|----------|
| Local | Image (8-bit) | 20×20 | 15.343× |
| Local | Image (16-bit) | 20×20 | 12.641× |
| Local | Image (8-bit) | 1200×1200 | 9.083× |
| Remote | Image (8-bit) | 881×638 | 10.894× |
| Remote | Image (8-bit) | 1136×816 | 9.374× |
| Remote | Scalar | N/A | 29.731× |

## Summary

The Rust serialisation extension consistently outperforms the Python implementation across all tested workloads.

Observed improvements include:

- ~9-15× faster serialisation for image data.
- ~30× faster serialisation for scalar values.
- Low run-to-run variance across benchmark executions.

These measurements include the cost of converting Python objects into their Rust representations, meaning the reported speedups reflect the end-to-end cost of serialisation rather than isolated serialisation performance.