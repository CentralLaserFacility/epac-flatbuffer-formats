# FlatBuffers schema reference

This page describes the payload structures, data types and metadata for the schemas provided by this package. The canonical FlatBuffers
definitions are:

| Schema | Definition |
| --- | --- |
| `pva0` | [`pva0.fbs`](https://github.com/CentralLaserFacility/epac-flatbuffer-formats/blob/development/schemas/pva0.fbs) |
| `f142` | [`f142_logdata.fbs`](https://github.com/CentralLaserFacility/epac-flatbuffer-formats/blob/development/schemas/f142_logdata.fbs) |
| `ADAr` | [`ADAr_area_detector_array.fbs`](https://github.com/CentralLaserFacility/epac-flatbuffer-formats/blob/development/schemas/ADAr_area_detector_array.fbs) |
| `wa00` | [`wa00_waveform.fbs`](https://github.com/CentralLaserFacility/epac-flatbuffer-formats/blob/development/schemas/wa00_waveform.fbs) |

See the [schema usage guide](../explanations/schema_details.md) for usage details.

## Common format

Each serializer returns a FlatBuffers buffer as `bytes`. Each schema has a file identifier,
allowing consumers to identify the format:

| Schema | File identifier | Root table |
| --- | --- | --- |
| `pva0` | `pva0` | `PVData` |
| `f142` | `f142` | `LogData` |
| `ADAr` | `ADAr` | `ADArray` |
| `wa00` | `wa00` | `WaveFormArray` |

The Python deserializers check the identifier before reading the root table
, meaning buffers from one schema must be read with that schema's deserializer.

---
(pva0)=
## `pva0`

`pva0` models EPICS PVAccess data using EPICS normative-type payloads. Its root
table is `PVData`, whose required `data` field is a union with these members:

| Payload | Purpose |
| --- | --- |
| `NTScalarAny` | Scalar or one-dimensional array value with optional descriptor, alarm, timestamp, display, and control metadata. |
| `NTNDArray` | Array or image, with optional codec, dimensions, unique ID, attributes, and associated metadata. |
| `NTTable` | Column-oriented table with labels and optional descriptor, alarm, timestamp, and display metadata. |
| `XYData` | Pair of `NTScalarAny` values named `x` and `y`. |

The root's optional `source_name`, `pulse_id`, and `effective_time_stamp` fields
identify the PV and carry additional event metadata.

Values in `NTScalarAny`, `NTNDArray`, and each `NTTable` column use `AnyT`.
`AnyT.value` is a union supporting the following scalar types and their array
forms:

- Boolean
- Signed and unsigned 8-, 16-, 32-, and 64-bit integers
- 32- and 64-bit floating-point numbers
- Strings

Additional metadata includes:

- `AlarmT`: alarm severity, status, and message.
- `TimeT`: seconds past epoch, nanoseconds, and user tag.
- `DisplayT`: display limits, description, units, precision, and display form.
- `ControlT`: control limits and minimum step.
- `DimensionT`: size, offset, full size, binning, and reverse flag.
- `NTAttribute`: a named value with tags, descriptor, alarm, time, and source.
- `CodecT`: codec name for encoded arrays.
- `PulseID`: pulse value and timestamp.

In the Python model these fields use camelCase names such as `sourceName`, while
the FlatBuffers definition uses snake_case such as `source_name`.

Rust serialization is supported for `PVData`. Deserialization is currently
available through the Python implementation.

---
(adar)=
## `ADAr`

`ADAr` is the AreaDetector array format. Its root table, `ADArray`, contains:

| Field | Type | Meaning |
| --- | --- | --- |
| `source_name` | string | Source name of the image or array. |
| `id` | int | Unique ID for the NDArray. |
| `timestamp` | ulong | Nanoseconds since the Unix epoch. |
| `dimensions` | vector of ulong | Array dimensions, with the fastest-varying dimension first. |
| `data_type` | `DType` | Element type of `data`. |
| `data` | vector of ubyte | Raw array data. |
| `attributes` | vector of `Attribute` | Optional metadata associated with the array. |

`DType` supports signed and unsigned 8-, 16-, 32-, and 64-bit integers, 32- and
64-bit floats, and `c_string`. Array dimensions are reversed relative to
NumPy's shape convention when stored and restored by the Python implementation.
For numeric arrays, `data` contains the flattened array bytes interpreted using
`data_type`.

Each `Attribute` contains a name, description, source, `DType`, and raw byte
data. The Python serializer accepts NumPy arrays, strings, integers, and floats
as attribute values. It accepts NumPy arrays or strings for the main payload.

---
(f142)=
## `f142`

`f142` represents a Channel Access log value. The root table `LogData` contains:

| Field | Type | Meaning |
| --- | --- | --- |
| `source_name` | string | Source identifier, typically a PV name. |
| `value` | `Value` union | Scalar or array payload. |
| `timestamp` | ulong | Nanoseconds since the Unix epoch; zero represents an invalid timestamp. |
| `status` | `AlarmStatus` | Alarm status; defaults to `NO_CHANGE`. |
| `severity` | `AlarmSeverity` | Alarm severity; defaults to `NO_CHANGE`. |
| `units` | string | Optional engineering units. |

`Value` supports signed and unsigned 8-, 16-, 32-, and 64-bit integers and
32- and 64-bit floats, as either scalars or arrays. Strings are not supported.
The Python serializer infers the FlatBuffers type from the value; use a NumPy
array with an explicit dtype when the intended type needs to be specified.

The alarm enums are defined in `f142_logdata.fbs`. `AlarmStatus` includes
`NO_ALARM`, read/write and limit conditions, and other Channel Access states.
`AlarmSeverity` includes `MINOR`, `MAJOR`, `NO_ALARM`, `INVALID`, and
`NO_CHANGE`.

---
(wa00)=
## `wa00`

`wa00` represents a waveform as paired x and y arrays. Its root table
`WaveFormArray` contains:

| Field | Type | Meaning |
| --- | --- | --- |
| `timestamp` | ulong | Optional y-data timestamp in nanoseconds since the Unix epoch. |
| `x_timestamp` | ulong | Optional x-data timestamp in nanoseconds since the Unix epoch. |
| `x_data_type`, `y_data_type` | `DType` | Element types for the corresponding arrays. |
| `x_data`, `y_data` | vectors of ubyte | Required raw array data. |
| `x_unit`, `y_unit` | strings | Optional units for each axis. |

`DType` supports signed and unsigned 8-, 16-, 32-, and 64-bit integers and
32- and 64-bit floats. The data vectors contain the arrays' raw bytes; the
associated dtype determines how to interpret them.

---
## Serializers and deserializers

The public Python functions for each schema are:

| Schema | Serializer | Deserializer | Python module |
| --- | --- | --- | --- |
| `pva0` | `serialise_data` | `deserialise_data` | `epac.flatbuffers.pva0_data` |
| `f142` | `serialise_f142` | `deserialise_f142` | `epac.flatbuffers.logdata_f142` |
| `ADAr` | `serialise_ADAr` | `deserialise_ADAr` | `epac.flatbuffers.area_detector_ADAr` |
| `wa00` | `serialise_wa00` | `deserialise_wa00` | `epac.flatbuffers.arrays_wa00` |

The Python deserializers accept `bytes` or `bytearray`. The
[API reference](ref) provides parameter and return-type details
for the Python functions and models.
