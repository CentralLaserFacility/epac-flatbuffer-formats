# Quickstart

This tutorial creates and round-trips a small `pva0` value without requiring any live EPICS PVs.

Steps are included using both the Python and Rust serialisers.

If you have not installed the package yet, follow the [installation instructions](installation.md).

## Create a value

Import `NTScalarAny` and `PVData` from the `data_types` module:

```python
from epac.flatbuffers.data_types import NTScalarAny, PVData
```

Construct a `PVData` object with a `NTScalarAny` payload:

```python
pv_data = PVData(
    sourceName="MY:PV:NAME",
    data=NTScalarAny(value=42),
)
```

`PVData` is the top-level model for the `pva0` schema. Here its `data` field contains an
`NTScalarAny` value.
Other supported payloads include `NTNDArray`, `NTTable`, and `XYData`.

```{note}
The `PVData` object also has optional `effectiveTimeStamp` and `pulseId` fields.
```

For guidance choosing a schema and details about the supported payloads, see
[Schema usage guide](../explanations/schema_details.md) and the
[schema reference](../reference/schema_reference.md).

## Serialise a value

The pure-Python serializer for the `pva0` schema is available from the
`pva0_data` module:

```python
from epac.flatbuffers.pva0_data import serialise_data
```

Serialise the `pv_data` object and write the result to a file:

```python
buffer = serialise_data(pv_data)
with open("buffer.bin", "wb") as file:
    file.write(buffer)
```

The serializer returns `bytes`, so open the file in binary
write mode (`"wb"`). To inspect the binary data in readable rows, run:

```shell
xxd -g1 buffer.bin
```

### Rust serializer

If you installed the optional Rust binding, you can use its `pva0` serializer
instead. See the [installation instructions](installation.md) for how to install
it. Replace the pure-Python import and serialization call with:

```python
from epac_flatbuffer_formats_rs import serialise_pv_data
buffer = serialise_pv_data(pv_data)
```

Both serializers produce the same format. Deserialisation is currently
available from the pure-Python module.

## Deserialise a value

Read the bytes back from the file in binary mode (`"rb"`) and pass them to
`deserialise_data`:

```python
from epac.flatbuffers.pva0_data import deserialise_data

with open("buffer.bin", "rb") as file:
    buffer = file.read()
restored = deserialise_data(buffer)
```

The deserialiser returns the same model structure. Access the restored value
through `restored.data.value`.

## Complete file

For example, save this as `quickstart.py`:

```python
from epac.flatbuffers.data_types import NTScalarAny, PVData
from epac.flatbuffers.pva0_data import serialise_data, deserialise_data

pv_data = PVData(
    sourceName="MY:PV:NAME",
    data=NTScalarAny(value=42),
)

buffer = serialise_data(pv_data)
with open("buffer.bin", "wb") as file:
    file.write(buffer)

with open("buffer.bin", "rb") as file:
    buffer = file.read()
restored = deserialise_data(buffer)

print(restored.sourceName)
print(restored.data.value)
```

Run your script:

```shell
python quickstart.py
```

You should see:

```text
MY:PV:NAME
42
```

To use the Rust serializer in this script, import `serialise_pv_data` from
`epac_flatbuffer_formats_rs` and replace `serialise_data(pv_data)` with
`serialise_pv_data(pv_data)`.