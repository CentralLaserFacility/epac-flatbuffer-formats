# Serialising EPICS Data

This tutorial uses p4p to read a live EPICS PV over PVAccess, serialise its
value using the `pva0` schema, and then deserialise it.

You will need the `epac-flatbuffer-formats` package and p4p. If you have not
installed the package yet, follow the [installation instructions](installation.md).
Install p4p separately if it is not already available in your environment:

```shell
pip install p4p
```

## Start the example PV server

The repository includes `examples/serve_pv.py`, which serves a scalar PV named
`EXAMPLE:PV` with the value `42`. From the repository root, start it in a
terminal and leave it running:

```shell
python3 examples/serve_pv.py
```

Run the serialisation example from a second terminal.

## Get a value from EPICS

Create a Python file called something like `serialise_epics.py`.

Import p4p's threaded client context and the `pva0` data model and serialiser:

```python
from p4p.client.thread import Context

from epac.flatbuffers.data_types import NTScalarAny, PVData
from epac.flatbuffers.pva0_data import deserialise_data, serialise_data
```

Set `pv_name` to the example PV served by the script above. It returns an EPICS
`NTScalar`. To use another accessible PV, replace `EXAMPLE:PV` with its name.

```python
pv_name = "EXAMPLE:PV"

# Keep the normative-type structure so its value and metadata are both available.
context = Context("pva", nt=False)
epics_value = context.get(pv_name)
```

With `nt=False`, p4p returns the normative-type structure instead of unwrapping
it to just the PV's value. Convert that structure to a dictionary and use it to
create an `NTScalarAny` model. `PVData` adds the PV name required by the
`pva0` schema:

```python
pv_data = PVData(
    sourceName=pv_name,
    data=NTScalarAny(**epics_value.todict()),
)
```

`NTScalarAny` supports scalar and scalar-array values. For other supported
normative types, use the matching model (`NTNDArray`, `NTTable`, or `XYData`)
from `epac.flatbuffers.data_types`.

## Serialise and deserialise the value

Serialise the `PVData` object to a FlatBuffers byte string:

```python
buffer = serialise_data(pv_data)
```

The buffer is binary data, so it will display as bytes rather than readable
text. Deserialize it and access the original value:

```python
restored = deserialise_data(buffer)
print(restored.sourceName)
print(restored.data.value)
```

````{note}
This serialisation can be done with the rust bindings.
Replace the `serialise_data` import and call with:
```python
from epac_flatbuffer_formats_rs import serialise_pv_data
buffer = serialise_pv_data(pv_data)
```
````

## Complete file

Your complete file should look like this:

```python
from p4p.client.thread import Context

from epac.flatbuffers.data_types import NTScalarAny, PVData
from epac.flatbuffers.pva0_data import deserialise_data, serialise_data

pv_name = "EXAMPLE:PV"
context = Context("pva", nt=False)
epics_value = context.get(pv_name)

pv_data = PVData(
    sourceName=pv_name,
    data=NTScalarAny(**epics_value.todict()),
)

buffer = serialise_data(pv_data)
restored = deserialise_data(buffer)

print(restored.sourceName)
print(restored.data.value)
```

Run the script:

```shell
python serialise_epics.py
```

It prints `EXAMPLE:PV` and its value, `42`.
