# Copied from https://github.com/ess-dmsc/python-streaming-data-types
# Upstream commit 3c2564cd6d

from collections import namedtuple
from typing import Any, Dict, Tuple, Union

import flatbuffers
import numpy as np

from .fbschemas.f142_logdata import LogData
from .fbschemas.f142_logdata.ArrayByte import (
    ArrayByte,
    ArrayByteAddValue,
    ArrayByteEnd,
    ArrayByteStart,
)
from .fbschemas.f142_logdata.ArrayDouble import (
    ArrayDouble,
    ArrayDoubleAddValue,
    ArrayDoubleEnd,
    ArrayDoubleStart,
)
from .fbschemas.f142_logdata.ArrayFloat import (
    ArrayFloat,
    ArrayFloatAddValue,
    ArrayFloatEnd,
    ArrayFloatStart,
)
from .fbschemas.f142_logdata.ArrayInt import (
    ArrayInt,
    ArrayIntAddValue,
    ArrayIntEnd,
    ArrayIntStart,
)
from .fbschemas.f142_logdata.ArrayLong import (
    ArrayLong,
    ArrayLongAddValue,
    ArrayLongEnd,
    ArrayLongStart,
)
from .fbschemas.f142_logdata.ArrayShort import (
    ArrayShort,
    ArrayShortAddValue,
    ArrayShortEnd,
    ArrayShortStart,
)
from .fbschemas.f142_logdata.ArrayUByte import (
    ArrayUByte,
    ArrayUByteAddValue,
    ArrayUByteEnd,
    ArrayUByteStart,
)
from .fbschemas.f142_logdata.ArrayUInt import (
    ArrayUInt,
    ArrayUIntAddValue,
    ArrayUIntEnd,
    ArrayUIntStart,
)
from .fbschemas.f142_logdata.ArrayULong import (
    ArrayULong,
    ArrayULongAddValue,
    ArrayULongEnd,
    ArrayULongStart,
)
from .fbschemas.f142_logdata.ArrayUShort import (
    ArrayUShort,
    ArrayUShortAddValue,
    ArrayUShortEnd,
    ArrayUShortStart,
)
from .fbschemas.f142_logdata.Byte import (
    Byte,
    ByteAddValue,
    ByteEnd,
    ByteStart,
)
from .fbschemas.f142_logdata.Double import (
    Double,
    DoubleAddValue,
    DoubleEnd,
    DoubleStart,
)
from .fbschemas.f142_logdata.Float import (
    Float,
    FloatAddValue,
    FloatEnd,
    FloatStart,
)
from .fbschemas.f142_logdata.Int import (
    Int,
    IntAddValue,
    IntEnd,
    IntStart,
)
from .fbschemas.f142_logdata.Long import (
    Long,
    LongAddValue,
    LongEnd,
    LongStart,
)
from .fbschemas.f142_logdata.Short import (
    Short,
    ShortAddValue,
    ShortEnd,
    ShortStart,
)
from .fbschemas.f142_logdata.UByte import (
    UByte,
    UByteAddValue,
    UByteEnd,
    UByteStart,
)
from .fbschemas.f142_logdata.UInt import (
    UInt,
    UIntAddValue,
    UIntEnd,
    UIntStart,
)
from .fbschemas.f142_logdata.ULong import (
    ULong,
    ULongAddValue,
    ULongEnd,
    ULongStart,
)
from .fbschemas.f142_logdata.UShort import (
    UShort,
    UShortAddValue,
    UShortEnd,
    UShortStart,
)
from .fbschemas.f142_logdata.Value import Value
from .utils import check_schema_identifier

# Re-exports
from .fbschemas.f142_logdata.AlarmSeverity import AlarmSeverity as AlarmSeverity
from .fbschemas.f142_logdata.AlarmStatus import AlarmStatus as AlarmStatus

FILE_IDENTIFIER = b"f142"


def _complete_buffer(
    builder,
    timestamp_unix_ns: int,
    alarm_status: Union[int, None] = None,
    alarm_severity: Union[int, None] = None,
) -> bytes:
    LogData.LogDataAddTimestamp(builder, timestamp_unix_ns)

    if alarm_status is not None:
        LogData.LogDataAddStatus(builder, alarm_status)
        # Only include severity if status was provided, it would be meaningless by itself
        if alarm_severity is not None:
            LogData.LogDataAddSeverity(builder, alarm_severity)

    log_msg = LogData.LogDataEnd(builder)

    builder.Finish(log_msg, file_identifier=FILE_IDENTIFIER)
    return bytes(builder.Output())


def _setup_builder(source_name: str) -> Tuple[flatbuffers.Builder, int]:
    builder = flatbuffers.Builder(1024)
    builder.ForceDefaults(True)
    source = builder.CreateString(source_name)
    return builder, source


def _serialise_byte(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    ByteStart(builder)
    ByteAddValue(builder, data.item())
    value_position = ByteEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.Byte)


def _serialise_bytearray(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    array_offset = builder.CreateNumpyVector(data)
    ArrayByteStart(builder)
    ArrayByteAddValue(builder, array_offset)
    value_position = ArrayByteEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.ArrayByte)


def _serialise_ubyte(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    UByteStart(builder)
    UByteAddValue(builder, data.item())
    value_position = UByteEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.UByte)


def _serialise_ubytearray(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    array_offset = builder.CreateNumpyVector(data)
    ArrayUByteStart(builder)
    ArrayUByteAddValue(builder, array_offset)
    value_position = ArrayUByteEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.ArrayUByte)


def _serialise_short(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    ShortStart(builder)
    ShortAddValue(builder, data.item())
    value_position = ShortEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.Short)


def _serialise_shortarray(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    array_offset = builder.CreateNumpyVector(data)
    ArrayShortStart(builder)
    ArrayShortAddValue(builder, array_offset)
    value_position = ArrayShortEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.ArrayShort)


def _serialise_ushort(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    UShortStart(builder)
    UShortAddValue(builder, data.item())
    value_position = UShortEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.UShort)


def _serialise_ushortarray(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    array_offset = builder.CreateNumpyVector(data)
    ArrayUShortStart(builder)
    ArrayUShortAddValue(builder, array_offset)
    value_position = ArrayUShortEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.ArrayUShort)


def _serialise_int(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    IntStart(builder)
    IntAddValue(builder, data.item())
    value_position = IntEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.Int)


def _serialise_intarray(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    array_offset = builder.CreateNumpyVector(data)
    ArrayIntStart(builder)
    ArrayIntAddValue(builder, array_offset)
    value_position = ArrayIntEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.ArrayInt)


def _serialise_uint(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    UIntStart(builder)
    UIntAddValue(builder, data.item())
    value_position = UIntEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.UInt)


def _serialise_uintarray(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    array_offset = builder.CreateNumpyVector(data)
    ArrayUIntStart(builder)
    ArrayUIntAddValue(builder, array_offset)
    value_position = ArrayUIntEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.ArrayUInt)


def _serialise_long(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    LongStart(builder)
    LongAddValue(builder, data.item())
    value_position = LongEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.Long)


def _serialise_longarray(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    array_offset = builder.CreateNumpyVector(data)
    ArrayLongStart(builder)
    ArrayLongAddValue(builder, array_offset)
    value_position = ArrayLongEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.ArrayLong)


def _serialise_ulong(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    ULongStart(builder)
    ULongAddValue(builder, data.item())
    value_position = ULongEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.ULong)


def _serialise_ulongarray(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    array_offset = builder.CreateNumpyVector(data)
    ArrayULongStart(builder)
    ArrayULongAddValue(builder, array_offset)
    value_position = ArrayULongEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.ArrayULong)


def _serialise_float(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    FloatStart(builder)
    FloatAddValue(builder, data.item())
    value_position = FloatEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.Float)


def _serialise_floatarray(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    array_offset = builder.CreateNumpyVector(data)
    ArrayFloatStart(builder)
    ArrayFloatAddValue(builder, array_offset)
    value_position = ArrayFloatEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.ArrayFloat)


def _serialise_double(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    DoubleStart(builder)
    DoubleAddValue(builder, data.item())
    value_position = DoubleEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.Double)


def _serialise_doublearray(builder: flatbuffers.Builder, data: np.ndarray, source: int):
    array_offset = builder.CreateNumpyVector(data)
    ArrayDoubleStart(builder)
    ArrayDoubleAddValue(builder, array_offset)
    value_position = ArrayDoubleEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.ArrayDouble)


_map_scalar_type_to_serialiser = {
    np.dtype("byte"): _serialise_byte,
    np.dtype("ubyte"): _serialise_ubyte,
    np.dtype("int8"): _serialise_byte,
    np.dtype("int16"): _serialise_short,
    np.dtype("int32"): _serialise_int,
    np.dtype("int64"): _serialise_long,
    np.dtype("uint8"): _serialise_ubyte,
    np.dtype("uint16"): _serialise_ushort,
    np.dtype("uint32"): _serialise_uint,
    np.dtype("uint64"): _serialise_ulong,
    np.dtype("float32"): _serialise_float,
    np.dtype("float64"): _serialise_double,
}

_map_array_type_to_serialiser = {
    np.dtype("byte"): _serialise_bytearray,
    np.dtype("ubyte"): _serialise_ubytearray,
    np.dtype("int8"): _serialise_bytearray,
    np.dtype("int16"): _serialise_shortarray,
    np.dtype("int32"): _serialise_intarray,
    np.dtype("int64"): _serialise_longarray,
    np.dtype("uint8"): _serialise_ubytearray,
    np.dtype("uint16"): _serialise_ushortarray,
    np.dtype("uint32"): _serialise_uintarray,
    np.dtype("uint64"): _serialise_ulongarray,
    np.dtype("float32"): _serialise_floatarray,
    np.dtype("float64"): _serialise_doublearray,
}


def serialise_f142(
    value: Any,
    source_name: str,
    timestamp_unix_ns: int = 0,
    alarm_status: Union[int, None] = None,
    alarm_severity: Union[int, None] = None,
) -> bytes:
    """
    Serialise value and corresponding timestamp as an f142 Flatbuffer message.
    Should automagically use a sensible type for value in the message, but if
    in doubt pass value in as a numpy ndarray of a carefully chosen dtype.

    :param value: can be a scalar or convertible to a 1-D ndarray; cannot be a string
    :param source_name: name of the data source
    :param timestamp_unix_ns: timestamp corresponding to value, e.g. when value was measured, in nanoseconds
    :param alarm_status: EPICS alarm status, best to provide using enum-like class defined in logdata_f142.AlarmStatus
    :param alarm_severity: EPICS alarm severity, best to provide using enum-like class defined in logdata_f142.AlarmSeverity
    """
    builder, source = _setup_builder(source_name)
    value = np.array(value)

    if value.ndim == 0:
        _serialise_value(builder, source, value, _map_scalar_type_to_serialiser)
    elif value.ndim == 1:
        _serialise_value(
            builder,
            source,
            value,
            _map_array_type_to_serialiser,
        )
    else:
        raise NotImplementedError("f142 only supports scalars or 1D array values")

    return bytes(
        _complete_buffer(builder, timestamp_unix_ns, alarm_status, alarm_severity)
    )


def _serialise_value(
    builder: flatbuffers.Builder,
    source: int,
    value: Any,
    serialisers_map: Dict,
):
    # We can use a dictionary to map most numpy types to one of the types defined in the flatbuffer schema
    # but we have to handle strings separately as there are many subtypes
    if np.issubdtype(value.dtype, np.unicode_) or np.issubdtype(
        value.dtype, np.string_
    ):
        # Strings were handled here once, but they were removed from the schema definition
        # This is left to give a nice clean error
        # All other string support code has been removed
        raise NotImplementedError("String serialisation has been removed")
    else:
        try:
            serialisers_map[value.dtype](builder, value, source)
        except KeyError:
            # There are a few numpy types we don't try to handle, for example complex numbers
            raise NotImplementedError(
                f"Cannot serialise data of type {value.dtype}, must use one of "
                f"{list(_map_scalar_type_to_serialiser.keys())}"
            )


_map_fb_enum_to_type: dict[int, type] = {
    Value.Byte: Byte,
    Value.UByte: UByte,
    Value.Short: Short,
    Value.UShort: UShort,
    Value.Int: Int,
    Value.UInt: UInt,
    Value.Long: Long,
    Value.ULong: ULong,
    Value.Float: Float,
    Value.Double: Double,
    Value.ArrayByte: ArrayByte,
    Value.ArrayUByte: ArrayUByte,
    Value.ArrayShort: ArrayShort,
    Value.ArrayUShort: ArrayUShort,
    Value.ArrayInt: ArrayInt,
    Value.ArrayUInt: ArrayUInt,
    Value.ArrayLong: ArrayLong,
    Value.ArrayULong: ArrayULong,
    Value.ArrayFloat: ArrayFloat,
    Value.ArrayDouble: ArrayDouble,
}


LogDataInfo = namedtuple(
    "LogDataInfo",
    ("value", "source_name", "timestamp_unix_ns", "alarm_status", "alarm_severity"),
)


def deserialise_f142(buffer: Union[bytearray, bytes]) -> LogDataInfo:
    check_schema_identifier(buffer, FILE_IDENTIFIER)

    log_data = LogData.LogData.GetRootAsLogData(buffer, 0)
    source_name = log_data.SourceName() if log_data.SourceName() else b""

    value_offset = log_data.Value()
    value_fb = _map_fb_enum_to_type[log_data.ValueType()]()
    value_fb.Init(value_offset.Bytes, value_offset.Pos)
    try:
        value = value_fb.ValueAsNumpy()
    except AttributeError:
        # Must be a scalar value then, so we'll get it like this
        value = np.array(value_fb.Value())

    timestamp = log_data.Timestamp()

    return LogDataInfo(
        value, source_name.decode(), timestamp, log_data.Status(), log_data.Severity()
    )


__all__ = [
    "serialise_f142",
    "deserialise_f142",
    "LogDataInfo",
    "AlarmStatus",
    "AlarmSeverity",
]
