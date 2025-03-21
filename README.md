# EPAC flatbuffer formats

This repository contains the canonical schema definitions for the flatbuffer
data formats used in the EPAC data management system, as well as Python code to
serialise and deserialise those formats.

`f142` and `ADAr` are heavily based on/copied from the
[ESS schemas][streaming-data-types] and [ESS code][python-streaming-data-types].
Code using the ESS `streaming_data_types` package should be able to be ported to
this package with few if any changes beyond the import path.

These, in addition to `wa00` will eventually be deprecated in favor of the singlular `pva0`
schema.

## Getting started

The package can be installed through `pip` as usual, although it is not
(currently) available on PyPI.  Clone this repository, set up a virtual
environment, and run `pip install .`.

To add this repository as a dependency to another project, you need to use pip's
support for git URLs. For example, you can add the following to your
`pyproject.toml`:

```toml
dependencies = [
    "epac-flatbuffer-formats @ git+https://github.com/CentralLaserFacility/epac-flatbuffer-formats@v0.2.0",
]
```

Each data format can be serialised and deserialised in a similar way. For
example, for `f142` (for recording values from a single PV):

```python
import time

from epac.flatbuffers.logdata_f142 import (
    deserialise_f142,
    serialise_f142,
    AlarmStatus,
    AlarmSeverity,
)

encoded_value = serialise_f142(42,
    source_name="MY:PV:NAME",
    timestamp_unix_ns=time.time() * 1e9,
    alarm_status=AlarmStatus.NO_ALARM,
    alarm_severity=AlarmSeverity.NO_ALARM,
)

...

decoded_value = deserialise_f142(buf)
print(decoded_value.value)
```

Note that each of these will have different arguments, in particular for `pva0` a PVData object
as defined in data_types.py is expected.

## Currently supported schemas and details

### f142
This is intended for scalar and array values from channel access with limited metadata.

#### Implementation Details
f142 is defined in the schema as a structure with the following fields:
- source_name: a string value identifying source
- value: main value of the pv in question, which can be any non string scalar
- timestamp: nanoseconds past epoch
- status: an enum representing alarm_status, details are in the schema
- schema: an enum representing alarm_severity, details are in the schema
- units: units of the value

For python:
This kind of data is serialised using the `serialise_f142` function, which takes each field as an
argument.
The bytes can be deserialised using the corresponding `deserialise_f142`.

As value can take multiple data types it is implemented as a Value union, made of tables of the
different standard types and arrays. This requires an extra serialization step, where NumPy ndarray
dtypes are used to map the received value to the corresponding type for serialization. This is
also encoded in the byte string which is used during the deserialisation.

### ADAr
This is intended for image data from AreaDetector via ADPluginKafka with limited metadata.

#### Implementation Details
ADAr is defined in the schema as a structure with the following fields:
- source_name: a string value identifying source
- id: a unique integer id
- timestamp: nanoseconds past epoch
- dimensions: an array containing details on the dimensions of the image
- data_type: type of the data stored in the array
- data: a raw bytes array
- attribute: these are extra metadata values, with each having name, description, source, data_type
and data fields

For python:
This kind of data is serialised using the `serialise_ADAr` function, which takes each field as an
argument.
The bytes can be deserialised using the corresponding `deserialise_ADAr`.

### wa00
This is intended for waveform data from channel access via two PVs with limited metadata.

#### Implementation Details
wa00 is defined in the schema as a structure with the following fields:

timestamp: nanoseconds past epoch for the last y update
x_timestamp: nanoseconds past epoch for the last x update
x_data_type: type of the data stored in the x_data array
y_data_type: type of the data stored in the y_data array
x_data: elements in the x array
y_data: elements in the y array
x_unit: units of the x array
y_unit: units of the y array

For python:
This kind of data is serialised using the `serialise_wa00` function, which takes each field as an
argument.
The bytes can be deserialised using the corresponding `deserialise_wa00`.


### pva0
This is intended for various types of data from pv access. There is currently support (based
on the EPICS V4 [normative types][normative-types]) for `NTScalarAny`, `NTNDArray` and `NTTable`.

#### Implementation Details
This schema was built based on the EPICS V4 [normative types][normative-types]. A `PVData` object is defined
which contains the following fields:
- data: the value of the PV as sent from pv access, in the form of one of the supported normative
types
- source_name: a string value identifying source

Currently `NTScalarAny` is used to handle both `NTScalar` and `NTScalarArray` types of data. `NTNDArray` is used for AreaDetector/Image data.
NTTable` is also supported for any potential use cases.

For python:
To assist with and validate the use of these FlatBuffers, Pydantic-based classes have been defined to
mimic the schema. Serialization and deserialization are performed using these classes. Specifically, a
PVData object (defined in data_types.py) should be passed to serialise_data when using pva0.`deserialise_data`
can be used to decode the bytes into a `PVData` object.

Additionally there are some special considerations made for more optimal usage:
- Alarm status and severity are handled as enums, as they have standard values.
- Enums such as display form are not handled via EnumT as per the normative types specification, rather
they use the style of flatbuffer enums.
- To convert between the case of Alarm enums, and the case of display form, they pydantic objects come
with parser support, which formats the data as required.

### ca_to_pva
ca_to_pva contains the CatoNTConverter class, which has functionality to convert data received from
channel access into a resultant pydantic `PVData` object which can then be used with `pva0`. This
supports being passed both a dictionary as well as corresponding custom types (eg. `CAScalarAny`) into
the corresponding convert_scalar or convert_waveform (not yet implemented) functions.

## Comparison with upstream for f142 and ADAr

The "upstreams" for this project are two ESS projects:
[`streaming-data-types`][streaming-data-types] and
[`python-streaming-data-types`][python-streaming-data-types]. Specific schemas
that will or might be used in EPAC have been copied into this repository, to
which EPAC-specific schemas have been added. This repository then serves as a
canonical location for all the schemas used in EPAC.

Unlike upstream, the Python support code is stored in the same repository, which
helps keep our generated code in sync with the schema definitions. The Python
code taken from upstream has been modified as necessary to pass our CI steps.

Where there is overlap, we aim to maintain compatibility with upstream, so that
any code using the Python [`streaming_data_types`][python-streaming-data-types]
package (`ess-streaming-data-types` on PyPI) can be adapted to use this package
with little effort beyond changing the import paths.

### Major differences with upstream for f142 and ADAr

Most schemas present in upstream are missing. At the time of writing, only
`f142` and `ADAr` have been kept.

At the time of writing,
[`python-streaming-data-types`][python-streaming-data-types] allows strings and
string arrays to be serialied to `f142`. As the string variants have been
removed from the [`streaming-data-types`][streaming-data-types] version of the
`f142` schema, we have also removed support for string serialisation.

## Development

There are four main bodies of code. Each schema should have:

- A definition in `schemas/`. The name should start with the file identifier
- Generated code in `src/epac/flatbuffers/fbschemas`. The subfolder containing
  the generated code should have the same name as the schema file
- Higher-level bindings under `src/epac/flatbuffers`. The name of the module
  should contain the file identifier, but is otherwise flexible. User code
  should not need to import anything from the generated code - useful enum
  definitions should be re-exported.
- Tests in `tests/test_<file_id>.py`

Code generated by a specific version of the Flatbuffers compiler `flatc` is
committed to the repository as a convenience. You won't need to worry about this
unless you're adding or modifying schemas or need to change how code is
generated. However, code under `src/epac/flatbuffers/fbschemas` must not be
modified by hand. See below for more details on
[how generated code is handled](#generated-code).

### Setup

Common development tasks can be automated using the included `dev.py` script.
To set up a virtual environment for development (in `.venv/`), run:

```shell
$ ./dev.py setup venv
```

Once that has been done, you can use `./dev.py run` to run any command in that
virtual environment. A number of other commands are supported: see `./dev.py
--help`.

To set up a Git pre-commit hook, run:

```shell
$ ./dev.py setup hooks
```

This should prevent you from making commits that fail linting. You can run the
pre-commit checks without making a commit by running:

```shell
$ ./dev.py pre-commit
```

But note that the real pre-commit hook will check the exact code that will be
committed by first stashing any unstaged changes or untracked files, so you
may not get exactly the same results.

### Generated code

Generated code must be generated by a specific version of `flatc`, then a number
of custom post-processing steps are needed. This is all handled by
`./dev.py schema-generate`. This in turn requires the correct version of `flatc`
to be installed with `./dev.py setup flatc`, which in turn requires the venv to
be set up.

Therefore, to regenerate schema definitions from a freshly checked-out
repository, you will need to run the following steps:

```shell
$ ./dev.py setup venv
$ ./dev.py setup flatc
$ ./dev.py schema-generate
```

A dedicated CI job checks that the generated code committed to the repository
matches what would be generated by a fresh invocation of
`./dev.py schema-generate`. You should only need to regenerate the code (and
hence install `flatc`) if you are modifying the schema definitions or the
generation process.

[streaming-data-types]: https://github.com/ess-dmsc/streaming-data-types
[python-streaming-data-types]: https://github.com/ess-dmsc/python-streaming-data-types
[normative-types]: https://docs.epics-controls.org/en/latest/pv-access/Normative-Types-Specification.html
