# How to migrate to `pva0`

The `f142`, `ADAr`, and `wa00` schemas are deprecated.

You should migrate when your data fits one of the payload types supported by `pva0`,
keep the old schema if the data cannot be represented without losing information.

## Map the old payload

`pva0` wraps each value in a `PVData` object. Choose the payload model that
matches your data:

| Existing data | `pva0` payload |
| --- | --- |
| `f142` scalar or array | `NTScalarAny` |
| `ADAr` image | `NTNDArray` |
| `wa00` x/y waveform | `XYData`, with `NTScalarAny` for each axis |

Move the value and any relevant metadata into the matching fields: for example,
timestamps into `TimeT`, alarms into `AlarmT`, and units and display limits into
`DisplayT`. Preserve array shape, element type, and axis order.

The schemas are not cross compatible.

## Create and serialise a `PVData`

Replace the old schema-specific serialiser call with construction of a `PVData`
and a call to `serialise_data`. For example, for a scalar:

```python
from epac.flatbuffers.data_types import NTScalarAny, PVData
from epac.flatbuffers.pva0_data import serialise_data

pv_data = PVData(
    sourceName="MY:PV:NAME",
    data=NTScalarAny(value=42),
)
buffer = serialise_data(pv_data)
```

Use `NTNDArray`, `NTTable`, or `XYData` instead when those better fit the data.
For more complete examples, see the [quickstart](../get_started/quickstart.md)
and [EPICS serialisation guide](../get_started/serialise_epics.md).
