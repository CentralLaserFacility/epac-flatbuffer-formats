# EPAC flatbuffer formats

This repository contains the canonical schema definitions for the flatbuffer
data formats used in the EPAC data management system.

It comprises:

1. Flatbuffers schema definitions (`/schemas`)
2. A Python library for serialisation and deserialisation of all schemas (`/src`)
3. A set of Rust crates providing support for serialising the `pva0` schema (`/rust`)

The `f142` and `ADAr` schemas are heavily based on/copied from the
[ESS schemas][streaming-data-types] and [ESS code][python-streaming-data-types].
Code using the ESS `streaming_data_types` package should be able to be ported to
this package with few if any changes beyond the import path.

These, in addition to `wa00`, have been deprecated in favour of the
singular `pva0` schema.

## Getting started

The Python package can be installed through `pip` as usual, although it is not
(currently) available on PyPI. Clone this repository, set up a virtual
environment, and run `pip install .`.

The Rust code is built into a wheel using maturin and is available as a GitHub
release.

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

serialised_data = serialise_f142(42,
    source_name="MY:PV:NAME",
    timestamp_unix_ns=time.time() * 1e9,
    alarm_status=AlarmStatus.NO_ALARM,
    alarm_severity=AlarmSeverity.NO_ALARM,
)

deserialised_data = deserialise_f142(serialised_data)
# attributes are accessible based on the fbs schema
alarm_severity = deserialised_data.severity
```

Note that each of these will have different arguments, in particular for `pva0` a `PVData` object
as defined in `data_types.py` is expected.

The Rust bindings are exposed as a Python module. They can be built and/or installed locally
with the commands defined in `dev.py` (see below), or managed manually with `maturin`.
At present, the only exposed entry point is `serialise_pv_data` for the `pva0` schema.
This should only need to be done if work is being done on it or if you need a new unreleased feature.

## Currently supported schemas and details

The currently supported schemas are `f142`, `ADAr`, `wa00` and `pva0`. For the former three,
the corresponding schema files define the fields contained within. For `pva0`, the EPICS V4
[normative-types] can be referred to for most cases with minimal changes. Refer to
[epac-forwarder] to see some direct use cases.

### pva0

This schema is intended for PVAccess data of various types.

#### Implementation Details

The `pva0` schema was built based on the EPICS V4 [normative-types]. A `PVData`
object contains the value of the PV as sent from PVAccess, in the form of one of the
supported data types, along with additional metadata such as the PV name (`source_name`).

`NTScalarAny` is used to handle both `NTScalar` and `NTScalarArray` payloads. `NTNDArray`
is used for AreaDetector/image data, and `NTTable` is also supported for relevant use cases.

A custom `XYData` type is also implemented; it is made up of `x` and `y` values, each of which
is intended to be an `NTScalarArray`.

#### Usage (Python)

To assist with and validate the use of these FlatBuffers, Pydantic-based classes
have been defined to mimic the schema. Serialisation and deserialisation are
performed using these classes to ensure standardisation.
- `epac.flatbuffers.pva0` exposes `serialise_data` and `deserialise_data`, which
  are pure Python implementations.
- `epac_flatbuffer_formats_rs` exposes a Python binding to Rust
  `serialise_pv_data`, which implements serialisation in Rust for `PVData`
  objects.

For convenience, enums are provided for alarm status, alarm severity, and display
format. These are automatically converted from the corresponding parts of the
normative types.

No deserialisation method is implemented in Rust, but FlatBuffers ensure that
data is readable across languages, so the pure Python implementation will
 deserialise data which was serialised using the Rust implementation.

##### Pure Python
```python

from p4p.client.thread import Context  # type: ignore
from epac.flatbuffers.data_types import PVData, NTScalarAny, NTNDArray, NTTable
from epac.flatbuffers.pva0_data import serialise_data, deserialise_data

# nt=False disables automatic unwrapping, which suits us as we are using our own structures
context = Context("pva", nt=False)
# This pv returns an NTScalar
pv_name = "DEV-EC-D-CAM-1:Stats1:Net_RBV"
pv_data = context.get(pv_name)
pv_data_object = PVData(
    data=NTScalarAny(**pv_data.todict()), sourceName=pv_name
)
serialised_data = serialise_data(pv_data_object)
deserialised_data = deserialise_data(serialised_data)
# attributes are accessible based on the fbs schema, but for pva0 it is better to refer to data_types.py
alarm_severity = deserialised_data.data.alarm.severity

# NTNDArray, NTTable, and XYData follow the same pattern.
# It is also possible to set up a monitor using a p4p subscription/monitor.
# An example of this can be found in epac-forwarder.

# It is also possible to directly use a dictionary as follows.

value = {
    "value": 1,
    "alarm": {"severity": 0, "status": 0, "message": "NO_ALARM"},
    "timeStamp": {
        "secondsPastEpoch": 1739946490,
        "nanoseconds": 410324754,
        "userTag": 0,
    },
}


pv_data_object = PVData(
    data=NTScalarAny(**value), sourceName=pv_name
)

```
##### Rust
```python

from p4p.client.thread import Context  # type: ignore
from epac.flatbuffers.data_types import PVData, NTScalarAny, NTNDArray, NTTable
from epac_flatbuffer_formats_rs import serialise_pv_data

# nt=False disables automatic unwrapping, which suits us as we are using our own structures
context = Context("pva", nt=False)
# This pv returns an NTScalar
pv_name = "DEV-EC-D-CAM-1:Stats1:Net_RBV"
pv_data = context.get(pv_name)
pv_data_object = PVData(
    data=NTScalarAny(**pv_data.todict()), sourceName=pv_name
)
serialised_data = serialise_pv_data(pv_data_object)

# deserialise as above
...

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
# value could also have been passed directly to convert_scalar, and it would do the object conversion
nt_scalar_object = CaToNtConverter().convert_scalar(ca_scalar_obj)
pv_data_object = PVData(data=nt_scalar_object, sourceName=self.pv_name)
```

### f142

The f142 schema is intended for scalar and array values from channel access.

#### Usage (Python)

```python
import time
import epics
from epac.flatbuffers.logdata_f142 import serialise_f142, deserialise_f142


pv = epics.PV(
    "EPAC-DEV:CAM1:stats1:Net_RBV",
    form="ctrl",
)

# a delay is added in to ensure connection in this example
time.sleep(1)
pv_data = pv.get_with_metadata()
serialised_data = serialise_f142(
    value=pv_data["value"],
    source_name=pv_data["pvname"],
    units=pv_data["units"],
    # pyepics gives a unix timestamp
    timestamp_unix_ns=int(pv_data["timestamp"] * 1e9),
    alarm_status=pv_data["status"],
    alarm_severity=pv_data["severity"],
)

deserialised_data = deserialise_f142(serialised_data)

# similarly it is possible to setup pv monitioring using a callback, this is what is done with the
# epac-forwarder
```

As the value can take multiple data types it is implemented as a Value union, made of tables of the
different standard types and arrays. This requires an extra serialization step, where NumPy ndarray
dtypes are used to map the received value to the corresponding type for serialization. This is
also encoded in the byte string which is used during the deserialisation.

Specifically value may be byte, ubyte, short, ushort, int, unint, long, ulong, float, double or equivalent arrays
of each of these types. However this is handled via casting to an numpy dtype so only those dtypes are actually
supported.

### ADAr

The ADAr schema is intended for image data from AreaDetector via [ADPluginKafka]. While direct serialisation
is possible, ADPluginKafka is the currently preferred usage.

#### Usage (Python)

```python
from epac.flatbuffers.area_detector_ADAr import (
    Attribute,
    deserialise_ADAr,
    serialise_ADAr,
)

serialised_data = serialise_ADAr(
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

deserialised_data = deserialise_ADAr(serialised_data)

# as described, since this serialiser was designed with ADPluginKafka in mind, it is not built to
# support pyepics out of the box, and the data would need significant preprocessing
```

### wa00

A *waveform* is made of two arrays of the same length, one with x co-ordinates and the other with
y co-ordinates. Examples include an optical spectrum and an oscilloscope trace.

The wa00 schema is intended for waveform data from channel access. Functionally this data will come
from two distinct pvs.

#### Usage (Python)

```python
import time
from datetime import datetime
import epics
from epac.flatbuffers.arrays_wa00 import serialise_wa00, deserialise_wa00


pv_x = epics.PV(
    "EPAC-DEV:CAM1:stats1:HistogramX_RBV",
    form="ctrl",
)

pv_y = epics.PV(
    "EPAC-DEV:CAM1:stats1:Histogram_RBV",
    form="ctrl",
)

# a delay is added in to ensure connection in this example
time.sleep(1)
pv_x_data = pv_x.get_with_metadata()
pv_y_data = pv_y.get_with_metadata()
serialised_data = serialise_wa00(
    values_x_array=pv_x_data["value"],
    values_y_array=pv_y_data["value"],
    x_timestamp=datetime.fromtimestamp(pv_x_data["timestamp"]),
    timestamp=datetime.fromtimestamp(pv_y_data["timestamp"]),
    x_unit=pv_x_data["units"],
    y_unit=pv_y_data["units"]
)

deserialised_data = deserialise_wa00(serialised_data)

# wa00 object is returned with accessible attributes
alarm_severity = deserialised_data.values_x_array

# as with f142 it is possible to setup pv monitioring using a callback; as this concerns two pvs,
# a decision will  have to be taken accordingly, in epac-forwarder this is done via y-value updates
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
string arrays to be serialised to `f142`. However, as the string variants have been
removed from the [`streaming-data-types`][streaming-data-types] version of the
`f142` schema, we have also removed support for string serialisation.

## Development

Code generated by a specific version of the Flatbuffers compiler `flatc` is
committed to the repository as a convenience. You won't need to worry about this
unless you're adding or modifying schemas or need to change how code is
generated. However, code under `src/epac/flatbuffers/fbschemas` or
`rust/epac-flatbuffer-formats/src/generated` must not be modified by hand. See
below for more details on [how generated code is handled](#generated-code).

#### Python
There are four main bodies of Python code. Each schema should have:

- A definition in `schemas/`. The name should start with the file identifier.
- Generated code in `src/epac/flatbuffers/fbschemas`. The subfolder containing
  the generated code should have the same name as the schema file.
- Higher-level bindings under `src/epac/flatbuffers`. The name of the module
  should contain the file identifier, but is otherwise flexible. User code
  should not need to import anything from the generated code; useful enum
  definitions should be re-exported.
- Tests in `tests/test_<file_id>.py`.

#### Rust
Rust code lives in individual crates in `rust/`. At the time of writing, there
are currently two crates: `epac-flatbuffers-derive/`, which provides a derive
macro to automatically generate the serialisation code, and
`epac-flatbuffer-formats-rs/`, which defines the Rust data structures and
implements the serialisation to FlatBuffers for the `pva0` schema.



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

##### Rust

Helpers are also provided for building and managing mixed Python/Rust crates.
To set up your Python bindings for Rust code, run:

```shell
$ ./dev.py setup rust-bindings
```

Other common commands include:

```shell
$ ./dev.py rust-develop   # install rust bindings in venv
$ ./dev.py rust-build     # build a wheel for rust bindings
$ ./dev.py rust-clean     # clean the current installed bindings
```

These helpers rely on the `maturin` package being installed and active in the
virtual environment. As such, it is possible to manually use these
commands for greater flexibility (see [maturin-docs](https://www.maturin.rs/)).


### Generated code

Generated code must be generated by a specific version of `flatc`, then a
number of custom post-processing steps are needed.

This is all handled by `./dev.py schema-generate`. This in turn requires
the correct version of `flatc` to be installed with `./dev.py setup flatc`,
which in turn requires the venv to be set up.

Therefore, to regenerate schema definitions from a freshly checked-out
repository, you will need to run the following steps:

```shell
$ ./dev.py setup venv
$ ./dev.py setup flatc
$ ./dev.py schema-generate # generated code
```

A dedicated CI job checks that the generated code committed to the repository
matches what would be generated by a fresh invocation of
`./dev.py schema-generate` and `./dev.py rust-schema-generate`. You should
only need to regenerate the code (and hence install `flatc`) if you are
modifying the schema definitions or the generation process.

## Overview of the Rust crates

The Rust workspace currently contains two crates:

### epac_flatbuffers_derive
This crate defines the `serialise` derive macro, which is used to automatically implement the
serialisation trait for the Rust data structures defined in `epac_flatbuffer_formats_rs`.

### epac_flatbuffer_formats_rs
This crate defines the Rust data structures and implements the serialisation trait used to write
FlatBuffers. It also exposes the Python binding entry point `serialise_pv_data`.

[streaming-data-types]: https://github.com/ess-dmsc/streaming-data-types
[python-streaming-data-types]: https://github.com/ess-dmsc/python-streaming-data-types
[normative-types]: https://docs.epics-controls.org/en/latest/pv-access/Normative-Types-Specification.html
[ADPluginKafka]: https://github.com/CentralLaserFacility/ADPluginKafka
[epac-forwarder]: https://github.com/CentralLaserFacility/epac-forwarder
