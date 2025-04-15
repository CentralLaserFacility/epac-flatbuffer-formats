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

decoded_value = deserialise_f142(encoded_value)
print(decoded_value.value)
```

Note that each of these will have different arguments, in particular for `pva0` a PVData object
as defined in data_types.py is expected.

## Currently supported schemas and details

The currently supported schemas are f142, ADAr, wa00 and pva0. For the former three, the corresponding
schema files define the fields contained within. For pva00 the EPICS V4 [normative types][normative-types]
can be referred to for most cases with minimal changes.

### f142

This is intended for scalar and array values from channel access.

#### Implementation Details

As the value can take multiple data types it is implemented as a Value union, made of tables of the
different standard types and arrays. This requires an extra serialization step, where NumPy ndarray
dtypes are used to map the received value to the corresponding type for serialization. This is
also encoded in the byte string which is used during the deserialisation.

#### Usage (Python)

```python
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

decoded_value = deserialise_f142(encoded_value)
```

### ADAr

This is intended for image data from AreaDetector via ADPluginKafka. While direct serialisation is
possible, ADPluginKafka is the currently preffered usage.

#### Usage (Python)

```python
from epac.flatbuffers.area_detectot_ADAr import (
    Attribute,
    deserialise_ADAr,
    serialise_ADAr,
)

encoded_value = serialise_f142(42,
    source_name="MY:PV:NAME",
    unique_id=1,
    timestamp=time.time() * 1e9,
    data=np.array([[1, 2, 3], [3, 4, 5]], dtype=np.uint64),
    attributes=[
                Attribute("name1", "desc1", "src1", "value"),
                Attribute("name2", "desc2", "src2", 11),
                Attribute("name3", "desc3", "src3", 3.14),
                Attribute("name4", "desc4", "src4", np.linspace(0, 10)),
            ],
)

decoded_value = deserialise_ADAr(encoded_value)
```

### wa00

This is intended for waveform data from channel access via two PVs.

#### Usage (Python)

```python
from epac.flatbuffers.arrays_wa00 import (
    deserialise_wa00,
    serialise_wa00,
)

encoded_value = serialise_wa00(
    values_x_array=np.array([1, 2, 3, 4, 5, 1], dtype=np.uint64),
    values_y_array=np.array([6, 7, 8, 9, 10, 6], dtype=np.uint64),
    timestamp=datetime.now(tz=timezone.utc),
    x_timestamp=datetime.now(tz=timezone.utc) - timedelta(minutes=5),
    y_unit="vs",
    x_unit="ss",
)

decoded_value = deserialise_wa00(encoded_value)
```

### pva0

This is intended for various types of data from pv access.

#### Implementation Details

This schema was built based on the EPICS V4 [normative types][normative-types]. A `PVData` object is defined
which contains the following fields:

- data: the value of the PV as sent from pv access, in the form of one of the supported normative
types
- source_name: the source of the data; for example, the name of a PV

Currently `NTScalarAny` is used to handle both `NTScalar` and `NTScalarArray` types of data. `NTNDArray` is used for AreaDetector/Image data.
NTTable` is also supported for any potential use cases.

#### Usage (Python)

To assist with and validate the use of these FlatBuffers, Pydantic-based classes have been defined to
mimic the schema. Serialization and deserialization are performed utilising these classes to ensure
standardisation.

Additionally there are some special considerations made for more optimal usage:

- Alarm status and severity are handled as enums, as they have standard values.
- Enums such as display form are not handled via EnumT as per the normative types specification, rather
they use the style of flatbuffer enums.
- To convert between the case of Alarm enums, and the case of display form, they pydantic objects come
with parser support, which formats the data as required.

```python
from epac.flatbuffers.pva0_data import (
    deserialise_data,
    serialise_data,
)
from epac.flatbuffers import data_types as dt

value = {
    "value": 1,
    "descriptor": "test nt scalar data",
    "alarm": {"severity": 0, "status": 0, "message": "NO_ALARM"},
    "timeStamp": {
        "secondsPastEpoch": 1739946490,
        "nanoseconds": 410324754,
        "userTag": 0,
    },
    "display": {
        "limitLow": 0.0,
        "limitHigh": 0.0,
        "description": "Application Directory",
        "units": "u",
        "precision": 0,
        "form": {
            "index": 0,
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
    "control": {"limitLow": 0.0, "limitHigh": 0.0, "minStep": 0.0},
}

nt_scalar_obj = dt.NTScalarAny(**value)
pv_data_obj = dt.PVData(data=nt_scalar_obj, source_name="some source name")
encoded_value = serialise_data(pv_data_obj)
decoded_value = deserialise_data(encoded_value)

value = {
    "value": np.array([91, 92, 93, 102, 103, 104], dtype=np.uint8),
    "codec": {"name": ""},
    "compressedSize": 6,
    "uncompressedSize": 6,
    "dimension": [
        {"size": 1, "offset": 0, "fullSize": 1, "binning": 1, "reverse": False},
        {"size": 6, "offset": 0, "fullSize": 6, "binning": 1, "reverse": False},
    ],
    "uniqueId": 16991836,
    "dataTimeStamp": {
        "secondsPastEpoch": 1740045680,
        "nanoseconds": 233594894,
        "userTag": 0,
    },
    "attribute": [
        {
            "name": "ColorMode",
            "value": 0,
            "descriptor": "Color mode",
            "sourceType": 0,
            "source": "Driver",
            "alarm": None,
            "time": None,
            "tags": ["tag1", "tag2"],
        }
    ],
    "descriptor": "",
    "alarm": {"severity": 0, "status": 0, "message": "NO_ALARM"},
    "timeStamp": {
        "secondsPastEpoch": 1740045680,
        "nanoseconds": 233594955,
        "userTag": 0,
    },
    "display": {
        "limitLow": 0.0,
        "limitHigh": 0.0,
        "description": "Example NDArray",
        "form": {
            "index": 0,
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
        "units": "pixels",
        "precision": 1,
    },
}

nt_ndarray_obj = dt.NTScalarAny(**value)
pv_data_obj = dt.PVData(data=nt_ndarray_obj, source_name="some source name")
encoded_value = serialise_data(pv_data_obj)
decoded_value = deserialise_data(encoded_value)

# In both of the above examples it is also possible to define individual components of the value using
# the corresponding pydantic types.
```

### ca_to_pva

ca_to_pva contains the CatoNTConverter class, which has functionality to convert data received from
channel access into a resultant pydantic `PVData` object which can then be used with `pva0`. This
supports being passed both a dictionary as well as corresponding custom types (eg. `CAScalarAny`) into
the corresponding convert_scalar or convert_waveform (not yet implemented) functions.

#### Usage (Python)

```python
from epac.flatbuffers.ca_to_pva import CaToNtConverter
from epac.flatbuffers import data_types as dt
value = {
    "value": 42.5,
    "pvname": "some pv name",
    "status": 1,
    "precision": 2,
    "units": "V",
    "severity": 0,
    "timestamp": 1713201234.567,
    "upper_disp_limit": 100.0,
    "lower_disp_limit": 0.0,
    "upper_ctrl_limit": 95.0,
    "lower_ctrl_limit": 5.0
}
ca_scalar_obj = dt.CAScalarAny(**value)
# value could also have been passed directly to convert_scalar
nt_scalar_object = CaToNtConverter().convert_scalar(ca_scalar_obj)
pv_data_object = PVData(data=nt_scalar_object, sourceName=self.pv_name)
```

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

At the time of writing,
[`python-streaming-data-types`][python-streaming-data-types] allows strings and
string arrays to be serialied to `f142`. However, as the string variants have been
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
