(schema-details)=
# Schema usage guide

This guide helps you choose a schema and shows how to serialise and deserialise
its data in Python. For exact payload fields, types, identifiers, and wire
details, see the [schema reference](../reference/schema_reference.md).

## Choose a schema

Use the format expected by the producer or consumer that exchanges your data.
For new EPICS PVAccess integrations, `pva0` is the recommended choice.

| Use case | Schema | Guidance |
| --- | --- | --- |
| EPICS PVAccess values, including scalars, arrays, tables, and images | `pva0` | Recommended for new development. Images use the `NTNDArray` payload. |
| Images exchanged through legacy AreaDetector integrations | `ADAr` | Use when working with an ADAr consumer such as [ADPluginKafka](https://github.com/CentralLaserFacility/ADPluginKafka). |
| Scalar or one-dimensional array log values from Channel Access | `f142` | Deprecated |
| A waveform represented by x and y arrays | `wa00` | Deprecated |

`ADAr` and `pva0` can both represent image data, but they are different
formats. Choose `ADAr` for an existing AreaDetector/ADPluginKafka workflow;
choose `pva0` when the consumer expects EPICS normative types or when starting
a new PVAccess integration. The `f142`, `ADAr`, and `wa00` schemas remain
available for compatibility and may be removed in a future major release.

## Serialise and deserialise `pva0`

The Python API takes a Pydantic model from `epac.flatbuffers.data_types` and
returns a FlatBuffers byte string. The deserialiser reconstructs the model:

```python
from epac.flatbuffers.data_types import NTScalarAny, PVData
from epac.flatbuffers.pva0_data import deserialise_data, serialise_data

pv_data = PVData(
    sourceName="MY:PV:NAME",
    data=NTScalarAny(value=42),
)

buffer = serialise_data(pv_data)
restored = deserialise_data(buffer)
print(restored.sourceName)
print(restored.data.value)
```

Replace `NTScalarAny` with `NTNDArray`, `NTTable`, or `XYData` when the payload
has that shape. For an image, for example, put the array and its normative-type
metadata in an `NTNDArray` and keep it inside `PVData`.

The Rust binding can also serialise `PVData`:

```python
from epac_flatbuffer_formats_rs import serialise_pv_data

buffer = serialise_pv_data(pv_data)
```

The Rust binding currently supports serialisation only. Use
`epac.flatbuffers.pva0_data.deserialise_data` in Python to read a buffer from
either serializer; both produce the same `pva0` format.

For a live PVAccess example using p4p, see
[Serialising EPICS Data](../get_started/serialise_epics.md).

## Use the legacy schemas

Each legacy schema has a dedicated serializer and deserializer. Pass the
resulting bytes to the matching deserializer:

```python
from datetime import datetime, timezone

import numpy as np

from epac.flatbuffers.area_detector_ADAr import deserialise_ADAr, serialise_ADAr
from epac.flatbuffers.arrays_wa00 import deserialise_wa00, serialise_wa00
from epac.flatbuffers.logdata_f142 import deserialise_f142, serialise_f142

# AreaDetector image data; timestamp is a datetime.
image_buffer = serialise_ADAr(
    source_name="MY:IMAGE:PV",
    unique_id=1,
    timestamp=datetime.now(timezone.utc),
    data=np.array([[1, 2, 3], [4, 5, 6]], dtype=np.uint16),
)
image = deserialise_ADAr(image_buffer)

# A Channel Access log scalar. The timestamp is nanoseconds since the Unix epoch.
log_buffer = serialise_f142(
    value=42.5,
    source_name="MY:SCALAR:PV",
    units="mm",
    timestamp_unix_ns=1739946490410324754,
)
log_value = deserialise_f142(log_buffer)

# A waveform: x and y are arrays, with optional timestamps and units.
waveform_buffer = serialise_wa00(
    values_x_array=np.array([0.0, 1.0], dtype=np.float32),
    values_y_array=np.array([10.0, 12.0], dtype=np.float32),
    x_unit="s",
    y_unit="V",
)
waveform = deserialise_wa00(waveform_buffer)
```

`ADAr` and `wa00` support fixed-width integer and floating-point NumPy dtypes;
`f142` supports its listed scalar and array types but not strings. Refer to the
[schema reference](../reference/schema_reference.md) for the supported types,
metadata, and encoding constraints.

### Channel Access integrations

For Channel Access scalar values that should use `pva0`, `CaToNtConverter`
converts a `CAScalarAny` model or a matching dictionary into an `NTScalarAny`.
The converted value can then be placed in a `PVData` object and serialized as
usual:

```python
from epac.flatbuffers.ca_to_pva import CaToNtConverter
from epac.flatbuffers.data_types import PVData
from epac.flatbuffers.pva0_data import serialise_data

ca_value = {
    "value": 42.5,
    "pvname": "MY:PV:NAME",
    "status": 1,
    "precision": 2,
    "units": "V",
    "severity": 0,
    "timestamp": 1713201234.567,
    "upper_disp_limit": 100.0,
    "lower_disp_limit": 0.0,
    "upper_ctrl_limit": 95.0,
    "lower_ctrl_limit": 5.0,
}
nt_scalar = CaToNtConverter().convert_scalar(ca_value)
pv_data = PVData(sourceName=ca_value["pvname"], data=nt_scalar)
buffer = serialise_data(pv_data)
```

The converter currently handles scalars only; Channel Access waveform
conversion is not implemented.
