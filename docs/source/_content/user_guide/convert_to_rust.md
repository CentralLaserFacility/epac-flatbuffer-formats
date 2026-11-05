# How to Convert to Rust Serialisation

The optional Rust binding can serialise `pva0` data faster than the pure-Python
implementation. See the [benchmark results](../reference/serialisation_performance.md).

```{note}
Rust serialisation supports only the `pva0` schema. If you use another schema,
see [How to migrate to `pva0`](migrate_to_pva0.md).
```

## Switch the serializer

Install the optional Rust binding in the same Python environment as the main
package. See the [installation guide](installation) for
release and development installation instructions.

If your code currently uses the Python serializer:

```python
from epac.flatbuffers.pva0_data import serialise_data

buffer = serialise_data(pv_data)
```

replace the import and call with:

```python
from epac_flatbuffer_formats_rs import serialise_pv_data

buffer = serialise_pv_data(pv_data)
```

The `PVData` object and resulting FlatBuffers bytes are unchanged, so existing
Python deserialisation continues to work:

```python
from epac.flatbuffers.pva0_data import deserialise_data

restored = deserialise_data(buffer)
```

---
### Tips and Tricks

#### Use the `as` Keyword

Instead of changing the function call, you can use the `as` keyword to import the Rust serialiser under the same name as the Python serialiser:

```python
from epac_flatbuffer_formats_rs import serialise_pv_data as serialise_data
```

This reduces the conversion to a single-line change, but may increase confusion because it is not immediately clear which serialiser is being used.

#### Retain Python as an Option

It may be necessary to support both Python and Rust serialisation.

This is best done by using import logic to assign the desired callable to a common variable. For example:

```python
FORCE_PYTHON = False  # perhaps set from a configuration file

if FORCE_PYTHON:
    from epac.flatbuffers.pva_data import serialise_data
    serialiser = serialise_data
else:
    from epac_flatbuffer_formats_rs import serialise_pv_data
    serialiser = serialise_pv_data

...

buffer = serialiser(pv_data)  # serialiser will be Rust in this case
```