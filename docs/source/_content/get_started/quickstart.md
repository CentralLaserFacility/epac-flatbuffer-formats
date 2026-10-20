# Quickstart

This tutorial creates and round-trips a small `pva0` value without requiring any live EPICS PVs.

Steps are included using both the Python and Rust serialisers.

If you have not installed the package yet, follow the [installation instructions](installation.md).

## Create a value

Create a python file and call it something like `quickstart.py`.

The first thing we want to do is create the object we want to serialise.

Import `NTScalarAny` and `PVData` from the `data_types` module:

```python
from epac.flatbuffers.data_types import NTScalarAny, PVData
```

We can then construct a `PVData` object with a `NTScalarAny` payload:

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

The following example uses the pure-Python serializer for the `pva0` schema.

### Pure Python

Import the `serialise_data` function:

``` python
from epac.flatbuffers.pva0_data import serialise_data
```

If you have the Rust binding installed, replace this import with
`from epac_flatbuffer_formats_rs import serialise_pv_data` and call
`serialise_pv_data(pv_data)` instead of `serialise_data(pv_data)`. The output is
the same, only the serializer implementation changes.

Each schema has its own serialisers and deserialisers which are exposed under the schema specific modules:
`area_Detector_ADAr`, `pva0_data`, `logdata_f142` and `arrays_wa00`.

Serialising our `pv_data` object:

```
buffer = serialise_data(pv_data)
```

You can examine the buffer by adding a print statement

```python
print(buffer)
```

and running the file:

```shell
$ python quickstart.py
```

The returned value is a binary FlatBuffers buffer, which is expected to look like a byte string rather than readable text.

```
b'\x18\x00\x00\x00pva0\x00\x00\x00\x00\x00\x00\n\x00\x10\x00\x0f\x00\x08\x00\x04\x00\n\x00\x00\x00\x0c\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x01\n\x00\x00\x00MY:PV:NAME\x00\x00\x08\x00\x0c\x00\x08\x00\x04\x00\x08\x00\x00\x00\x08\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\n\x00\t\x00\x04\x00\x08\x00\x00\x00\x0c\x00\x00\x00\x00\x08\x06\x00\x0c\x00\x04\x00\x06\x00\x00\x00*\x00\x00\x00\x00\x00\x00\x00'
```

## Deserialise a value

Deserialisation is (currently) only performed by the pure python module.
This is possible because both serializers use the same FlatBuffers schema.

Import the `deserialise_data` function from the `pva0_data` module and save the output to a variable

```python
from epac.flatbuffers.pva0_data import deserialise_data
restored = deserialise_data(buffer)
```

The deserialiser returns the same model structure, so you can access
the restored value through `restored.data.value`.

Add print statements:

```python
print(restored.sourceName)
print(restored.data.value)
```

## Complete file

Your complete file should look a little something like this:

```python
from epac.flatbuffers.data_types import NTScalarAny, PVData
from epac.flatbuffers.pva0_data import serialise_data, deserialise_data

# Rust serialiser:
# from epac_flatbuffer_formats_rs import serialise_pv_data
# buffer = serialise_pv_data(pv_data)

pv_data = PVData(
    sourceName="MY:PV:NAME",
    data=NTScalarAny(value=42),
)

buffer = serialise_data(pv_data)
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

Feel free to explore serialising other data, maybe even try using a different schema.