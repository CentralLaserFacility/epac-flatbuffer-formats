from functools import wraps
from typing import Callable, Optional, TypeVar

import flatbuffers
import numpy as np

import epac.flatbuffers.data_types as dt

from .fbschemas.pva0 import (
    Bool,
    Byte,
    UByte,
    Short,
    UShort,
    Int,
    UInt,
    Long,
    ULong,
    Float,
    Double,
    String,
    BoolArray,
    ByteArray,
    UByteArray,
    ShortArray,
    UShortArray,
    IntArray,
    UIntArray,
    LongArray,
    ULongArray,
    FloatArray,
    DoubleArray,
    StringArray,
    AnyT,
    AnyInner,
    EnumT,
    AlarmT,
    TimeT,
    DisplayT,
    ControlT,
    CodecT,
    DimensionT,
    Column,
    NTAttribute,
    NTScalarAny,
    NTNDArray,
    NTTable,
    PVType,
    PVData,
)


base_dtype_map = {
    np.dtype("bool"): (
        Bool,
        BoolArray,
        AnyInner.AnyInner.Bool,
        AnyInner.AnyInner.BoolArray,
    ),
    np.dtype("byte"): (
        Byte,
        ByteArray,
        AnyInner.AnyInner.Byte,
        AnyInner.AnyInner.ByteArray,
    ),
    np.dtype("int8"): (
        Byte,
        ByteArray,
        AnyInner.AnyInner.Byte,
        AnyInner.AnyInner.ByteArray,
    ),
    np.dtype("ubyte"): (
        UByte,
        UByteArray,
        AnyInner.AnyInner.UByte,
        AnyInner.AnyInner.UByteArray,
    ),
    np.dtype("uint8"): (
        UByte,
        UByteArray,
        AnyInner.AnyInner.UByte,
        AnyInner.AnyInner.UByteArray,
    ),
    np.dtype("int16"): (
        Short,
        ShortArray,
        AnyInner.AnyInner.Short,
        AnyInner.AnyInner.ShortArray,
    ),
    np.dtype("uint16"): (
        UShort,
        UShortArray,
        AnyInner.AnyInner.UShort,
        AnyInner.AnyInner.UShortArray,
    ),
    np.dtype("int32"): (
        Int,
        IntArray,
        AnyInner.AnyInner.Int,
        AnyInner.AnyInner.IntArray,
    ),
    np.dtype("uint32"): (
        UInt,
        UIntArray,
        AnyInner.AnyInner.UInt,
        AnyInner.AnyInner.UIntArray,
    ),
    np.dtype("int64"): (
        Long,
        LongArray,
        AnyInner.AnyInner.Long,
        AnyInner.AnyInner.LongArray,
    ),
    np.dtype("uint64"): (
        ULong,
        ULongArray,
        AnyInner.AnyInner.ULong,
        AnyInner.AnyInner.ULongArray,
    ),
    np.dtype("float32"): (
        Float,
        FloatArray,
        AnyInner.AnyInner.Float,
        AnyInner.AnyInner.FloatArray,
    ),
    np.dtype("float64"): (
        Double,
        DoubleArray,
        AnyInner.AnyInner.Double,
        AnyInner.AnyInner.DoubleArray,
    ),
}

map_dtype_to_scalar_fb = {k: v[0] for k, v in base_dtype_map.items()}
map_dtype_to_array_fb = {k: v[1] for k, v in base_dtype_map.items()}
map_dtype_to_any_scalar_enum = {k: v[2] for k, v in base_dtype_map.items()}
map_dtype_to_any_array_enum = {k: v[3] for k, v in base_dtype_map.items()}

map_any_scalar_enum_to_type = {
    AnyInner.AnyInner.Bool: Bool.Bool,
    AnyInner.AnyInner.Byte: Byte.Byte,
    AnyInner.AnyInner.UByte: UByte.UByte,
    AnyInner.AnyInner.Short: Short.Short,
    AnyInner.AnyInner.UShort: UShort.UShort,
    AnyInner.AnyInner.Int: Int.Int,
    AnyInner.AnyInner.UInt: UInt.UInt,
    AnyInner.AnyInner.Long: Long.Long,
    AnyInner.AnyInner.ULong: ULong.ULong,
    AnyInner.AnyInner.Float: Float.Float,
    AnyInner.AnyInner.Double: Double.Double,
    AnyInner.AnyInner.String: String.String,
}

map_any_array_enum_to_type = {
    AnyInner.AnyInner.BoolArray: BoolArray.BoolArray,
    AnyInner.AnyInner.ByteArray: ByteArray.ByteArray,
    AnyInner.AnyInner.UByteArray: UByteArray.UByteArray,
    AnyInner.AnyInner.ShortArray: ShortArray.ShortArray,
    AnyInner.AnyInner.UShortArray: UShortArray.UShortArray,
    AnyInner.AnyInner.IntArray: IntArray.IntArray,
    AnyInner.AnyInner.UIntArray: UIntArray.UIntArray,
    AnyInner.AnyInner.LongArray: LongArray.LongArray,
    AnyInner.AnyInner.ULongArray: ULongArray.ULongArray,
    AnyInner.AnyInner.FloatArray: FloatArray.FloatArray,
    AnyInner.AnyInner.DoubleArray: DoubleArray.DoubleArray,
    AnyInner.AnyInner.StringArray: StringArray.StringArray,
}

FILE_IDENTIFIER = b"pva0"

T = TypeVar("T")
U = TypeVar("U")


def safe_serialise(
    func: Callable[[flatbuffers.Builder, T], int],
) -> Callable[[flatbuffers.Builder, Optional[T]], int]:
    """
    A decorator that ensures serialisation functions return 0 if the data is None.

    Args:
        func: The serialisation function that takes a builder and data as arguments.

    Returns:
        A wrapped function that returns 0 if data is None; otherwise, it calls the original function.
    """

    @wraps(func)  # to preserve metadata
    def wrapper(builder: flatbuffers.Builder, data: Optional[T]) -> int:
        if data is None:
            return 0
        return func(builder, data)

    return wrapper


def safe_deserialise(func: Callable[[T], U]) -> Callable[[Optional[T]], Optional[U]]:
    """
    A decorator that ensures deserialisation functions return None if the buffer is None.

    Args:
        func: The deserialisation function that takes a buffer (bytes) as an argument.

    Returns:
        A wrapped function that returns None if the buffer is None; otherwise, it calls the original function.
    """

    @wraps(func)  # to preserve metadata
    def wrapper(buffer: Optional[T]) -> Optional[U]:
        if buffer is None:
            return None
        return func(buffer)

    return wrapper


# The four functions below serialize NumPy array data into FlatBuffers format.
# They all have the same argument types and return structures:
#
# **Arguments**:
# - `builder` (flatbuffers.Builder): The FlatBuffers builder used to construct the object.
# - `data` (np.ndarray): A NumPy array containing scalar or array values.
#
# **Returns**:
# - A tuple containing:
#   - The serialized data (FlatBuffers offset or vector).
#   - The corresponding FlatBuffers type (e.g., String, Int, etc.).
#   - The associated AnyInner type identifier (e.g., AnyInner.String, AnyInner.Int, etc.).
#
# The functions handle different data types:
# - `_serialise_string_scalar`: Serializes a single string scalar.
# - `_serialise_scalar`: Serializes a single scalar, supporting various types.
# - `_serialise_string_array`: Serializes an array of strings.
# - `_serialise_array`: Serializes an array of values, supporting various types.
#
# **Error Handling**:
# - If the data type is unsupported, a `TypeError` is raised for scalar and array types.


def _serialise_string_scalar(builder: flatbuffers.Builder, data: np.ndarray):
    return builder.CreateString(data.item()), String, AnyInner.AnyInner.String


def _serialise_scalar(builder: flatbuffers.Builder, data: np.ndarray):
    try:
        return (
            data.item(),
            map_dtype_to_scalar_fb[data.dtype],
            map_dtype_to_any_scalar_enum[data.dtype],
        )
    except KeyError:
        raise TypeError(f"Unsupported scalar dtype: {data.dtype}")


def _serialise_string_array(builder: flatbuffers.Builder, data: np.ndarray):
    internal_values_offsets = [builder.CreateString(item) for item in reversed(data)]
    StringArray.StringArrayStartValueVector(builder, len(data))
    for start_offset in internal_values_offsets:
        builder.PrependSOffsetTRelative(start_offset)
    return builder.EndVector(), StringArray, AnyInner.AnyInner.StringArray


def _serialise_array(builder: flatbuffers.Builder, data: np.ndarray):
    try:
        return (
            builder.CreateNumpyVector(data),
            map_dtype_to_array_fb[data.dtype],
            map_dtype_to_any_array_enum[data.dtype],
        )
    except KeyError:
        raise TypeError(f"Unsupported array dtype: {data.dtype}")


def serialise_any(builder: flatbuffers.Builder, data) -> int:
    """serialises an arbitrary object into a FlatBuffers Any union.

    Args:
        builder (flatbuffers.Builder): The FlatBuffers builder used to construct the object.
        data: The object to be serialised, which must be compatible with the Any union.

    Returns:
        The FlatBuffers offset for the serialised Any object.

    Raises:
        TypeError: If an attempt is made to serialize a multi-dimensional array (ndim > 1).
    """
    data = np.asarray(data)
    dtype = data.dtype

    if data.ndim == 0:  # Scalar
        if np.issubdtype(data.dtype, np.str_) or np.issubdtype(data.dtype, np.bytes_):
            data_start_offset, fb_type, enum_type = _serialise_string_scalar(
                builder, data
            )
        else:
            data_start_offset, fb_type, enum_type = _serialise_scalar(builder, data)
    elif data.ndim == 1:  # Array
        if np.issubdtype(dtype, np.str_) or np.issubdtype(dtype, np.bytes_):
            data_start_offset, fb_type, enum_type = _serialise_string_array(
                builder, data
            )
        else:
            data_start_offset, fb_type, enum_type = _serialise_array(builder, data)
    else:
        raise TypeError("Ony 0D and 1D Arrays are supported.")

    # Serialise the data using the FlatBuffer type
    fb_type.Start(builder)
    fb_type.AddValue(builder, data_start_offset)
    data_offset = fb_type.End(builder)

    AnyT.Start(builder)
    AnyT.AddValueType(builder, enum_type)
    AnyT.AddValue(builder, data_offset)
    return AnyT.End(builder)


def deserialise_any(buffer):
    """Deserialises the Any table from a FlatBuffer.

    Args:
        buffer: FlatBuffer object containing the serialised Any table.

    Returns:
        The deserialised scalar or array value.

    Raises:
        ValueError: If the data type is unsupported.
    """
    data_enum = buffer.ValueType()

    if data_enum in map_any_scalar_enum_to_type:
        data_fb = map_any_scalar_enum_to_type[data_enum]()
        data_offset = buffer.Value()
        data_fb.Init(data_offset.Bytes, data_offset.Pos)
        data = data_fb.Value()
        if data_enum == AnyInner.AnyInner.String:
            data = data.decode("utf-8")
        return data

    elif data_enum in map_any_array_enum_to_type:
        data_fb = map_any_array_enum_to_type[data_enum]()
        data_offset = buffer.Value()
        data_fb.Init(data_offset.Bytes, data_offset.Pos)
        if data_enum == AnyInner.AnyInner.StringArray:
            data = np.asarray(
                [str(data_fb.Value(n), "utf-8") for n in range(data_fb.ValueLength())]
            )
        else:
            data = data_fb.ValueAsNumpy()
        return data

    else:
        raise ValueError(f"Unsupported data type: {data_enum}")


@safe_serialise
def serialise_alarm(builder: flatbuffers.Builder, alarm_data: dt.AlarmT) -> int:
    """serialises an AlarmT table into FlatBuffers format.

    Args:
        builder (flatbuffers.Builder): The FlatBuffers builder used to construct the object.
        alarm_data (Optional[dt.AlarmT]): The AlarmT object containing alarm details.

    Returns:
        The FlatBuffers offset for the serialised AlarmT object.
    """
    message_offset = builder.CreateString(alarm_data.message)
    AlarmT.Start(builder)
    AlarmT.AddSeverity(builder, alarm_data.severity)
    AlarmT.AddStatus(builder, alarm_data.status)
    AlarmT.AddMessage(builder, message_offset)
    return AlarmT.End(builder)


@safe_deserialise
def deserialise_alarm(buffer: AlarmT.AlarmT) -> dt.AlarmT:
    """Deserialises the AlarmT table from a FlatBuffer.

    Args:
        buffer: FlatBuffer object containing the serialised AlarmT table.

    Returns:
        The deserialised Python object representation of the alarm data.
    """
    return dt.AlarmT(
        severity=buffer.Severity(),
        status=buffer.Status(),
        message=buffer.Message().decode("utf-8"),  # type: ignore
    )


@safe_serialise
def serialise_time(builder: flatbuffers.Builder, time_data: dt.TimeT) -> int:
    """serialises a TimeT table into FlatBuffers format.

    Args:
        builder (flatbuffers.Builder): The FlatBuffers builder used to construct the object.
        time_data (Optional[dt.TimeT]): The TimeT object containing time details.

    Returns:
        The FlatBuffers offset for the serialised TimeT object.
    """
    TimeT.Start(builder)
    TimeT.AddSecondsPastEpoch(builder, time_data.secondsPastEpoch)
    TimeT.AddNanoseconds(builder, time_data.nanoseconds)
    TimeT.AddUserTag(builder, time_data.userTag)
    return TimeT.End(builder)


@safe_deserialise
def deserialise_time(buffer: TimeT.TimeT) -> dt.TimeT:
    """Deserialises the TimeT table from a FlatBuffer.

    Args:
        buffer: FlatBuffer object containing the serialised TimeT table.

    Returns:
        The deserialised Python object representation of the time data.
    """
    return dt.TimeT(
        secondsPastEpoch=buffer.SecondsPastEpoch(),
        nanoseconds=buffer.Nanoseconds(),
        userTag=buffer.UserTag(),
    )


@safe_serialise
def serialise_display(builder: flatbuffers.Builder, display_data: dt.DisplayT) -> int:
    """serialises a DisplayT table into FlatBuffers format.

    Args:
        builder (flatbuffers.Builder): The FlatBuffers builder used to construct the object.
        display_data (Optional[dt.DisplayT]): The DisplayT object containing display details.

    Returns:
        The FlatBuffers offset for the serialised DisplayT object.
    """
    # Serialise EnumT (DisplayT.form)
    if display_data.form:
        form: dt.EnumT = display_data.form
        choices_offsets = [builder.CreateString(choice) for choice in form.choices]
        EnumT.StartChoicesVector(builder, len(choices_offsets))
        for choice_offset in reversed(choices_offsets):
            builder.PrependUOffsetTRelative(choice_offset)
        choices_vector_offset = builder.EndVector()
        EnumT.Start(builder)
        EnumT.AddIndex(builder, form.index)
        EnumT.AddChoices(builder, choices_vector_offset)
        form_offset = EnumT.EnumTEnd(builder)
    else:
        form_offset = 0
    # Serialise DisplayT
    description_offset = builder.CreateString(display_data.description)
    units_offset = builder.CreateString(display_data.units)
    DisplayT.Start(builder)
    DisplayT.AddLimitLow(builder, display_data.limitLow)
    DisplayT.AddLimitHigh(builder, display_data.limitHigh)
    DisplayT.AddDescription(builder, description_offset)
    DisplayT.AddUnits(builder, units_offset)
    DisplayT.AddPrecision(builder, display_data.precision)
    DisplayT.AddForm(builder, form_offset)
    return DisplayT.End(builder)


@safe_deserialise
def deserialise_display(buffer: DisplayT.DisplayT) -> dt.DisplayT:
    """Deserialises the DisplayT table from a FlatBuffer.

    Args:
        buffer: FlatBuffer object containing the serialised DisplayT table.

    Returns:
        The deserialised Python object representation of the display data.
    """
    # Deserialise the DisplayT form (EnumT)
    form_data = None
    form_buffer = buffer.Form()
    if form_buffer is not None:
        form_data = dt.EnumT(
            index=form_buffer.Index(),
            choices=[
                form_buffer.Choices(i).decode("utf-8")  # type: ignore
                for i in range(form_buffer.ChoicesLength())
            ],
        )

    # Deserialise the rest of the DisplayT fields
    return dt.DisplayT(
        limitLow=buffer.LimitLow(),
        limitHigh=buffer.LimitHigh(),
        description=buffer.Description().decode("utf-8"),  # type: ignore
        units=buffer.Units().decode("utf-8"),  # type: ignore
        precision=buffer.Precision(),
        form=form_data,
    )


@safe_serialise
def serialise_control(builder: flatbuffers.Builder, control_data: dt.ControlT) -> int:
    """serialises a ControlT table into FlatBuffers format.

    Args:
        builder (flatbuffers.Builder): The FlatBuffers builder used to construct the object.
        control_data (Optional[dt.ControlT]): The ControlT object containing control details.

    Returns:
        The FlatBuffers offset for the serialised ControlT object.
    """
    ControlT.Start(builder)
    ControlT.AddLimitLow(builder, control_data.limitLow)
    ControlT.AddLimitHigh(builder, control_data.limitHigh)
    ControlT.AddMinStep(builder, control_data.minStep)
    return ControlT.End(builder)


@safe_deserialise
def deserialise_control(buffer: ControlT.ControlT) -> dt.ControlT:
    """Deserialises the ControlT table from a FlatBuffer.

    Args:
        buffer: FlatBuffer object containing the serialised ControlT table.

    Returns:
        The deserialised Python object representation of the control data.
    """
    return dt.ControlT(
        limitLow=buffer.LimitLow(),
        limitHigh=buffer.LimitHigh(),
        minStep=buffer.MinStep(),
    )


@safe_serialise
def serialise_codec(builder: flatbuffers.Builder, codec_data: dt.CodecT) -> int:
    """serialises a CodecT table into FlatBuffers format.

    Args:
        builder (flatbuffers.Builder): The FlatBuffers builder used to construct the object.
        codec_data (Optional[dt.CodecT]): The CodecT object containing codec details.

    Returns:
        The FlatBuffers offset for the serialised CodecT object.
    """
    name_offset = builder.CreateString(codec_data.name)
    parameters_offset = serialise_any(builder, codec_data.parameters)
    CodecT.Start(builder)
    CodecT.AddName(builder, name_offset)
    CodecT.AddParameters(builder, parameters_offset)
    return CodecT.End(builder)


@safe_deserialise
def deserialise_codec(buffer: CodecT.CodecT) -> dt.CodecT:
    """Deserialises the CodecT table from a FlatBuffer.

    Args:
        buffer: FlatBuffer object containing the serialised CodecT table.

    Returns:
        The deserialised Python object representation of the codec data.
    """
    return dt.CodecT(
        name=buffer.Name().decode("utf-8"),  # type: ignore
        parameters=deserialise_any(buffer.Parameters()),
    )


@safe_serialise
def serialise_dimension(
    builder: flatbuffers.Builder, dimension_data: dt.DimensionT
) -> int:
    """Deserialises the DimensionT table from a FlatBuffer.

    Args:
        buffer: FlatBuffer object containing the serialised DimensionT table.

    Returns:
        The deserialised Python object representation of the dimension data.
    """
    DimensionT.Start(builder)
    DimensionT.AddSize(builder, dimension_data.size)
    DimensionT.AddOffset(builder, dimension_data.offset)
    DimensionT.AddFullSize(builder, dimension_data.fullSize)
    DimensionT.AddBinning(builder, dimension_data.binning)
    DimensionT.AddReverse(builder, dimension_data.reverse)
    return DimensionT.End(builder)


@safe_deserialise
def deserialise_dimension(buffer: DimensionT.DimensionT) -> dt.DimensionT:
    """Deserialises the DimensionT table from a FlatBuffer.

    Args:
        buffer: FlatBuffer object containing the serialised DimensionT table.

    Returns:
        The deserialised Python object representation of the DimensionT data.
    """
    return dt.DimensionT(
        size=buffer.Size(),
        offset=buffer.Offset(),
        fullSize=buffer.FullSize(),
        binning=buffer.Binning(),
        reverse=buffer.Reverse(),
    )


@safe_serialise
def serialise_ntattribute(
    builder: flatbuffers.Builder, ntattribute_data: dt.NTAttribute
) -> int:
    """serialises an NTAttribute table into FlatBuffers format.

    Args:
        builder (flatbuffers.Builder): The FlatBuffers builder used to construct the object.
        ntattribute_data (dt.NTAttribute): The NTAttribute object containing attribute details.

    Returns:
        The FlatBuffers offset for the serialised NTAttribute object.
    """
    name_offset = builder.CreateString(ntattribute_data.name)
    value_offset = serialise_any(builder, ntattribute_data.value)
    tags_offsets = [builder.CreateString(tag) for tag in ntattribute_data.tags]
    NTAttribute.StartTagsVector(builder, len(tags_offsets))
    for tag_offset in reversed(tags_offsets):
        builder.PrependUOffsetTRelative(tag_offset)
    tags_vector_offset = builder.EndVector()
    descriptor_offset = builder.CreateString(ntattribute_data.descriptor)
    alarm_offset = serialise_alarm(builder, ntattribute_data.alarm)
    time_offset = serialise_time(builder, ntattribute_data.time)
    source_offset = builder.CreateString(ntattribute_data.source)

    # Create NTAttribute
    NTAttribute.Start(builder)
    NTAttribute.AddName(builder, name_offset)
    NTAttribute.AddValue(builder, value_offset)
    NTAttribute.AddTags(builder, tags_vector_offset)
    NTAttribute.AddDescriptor(builder, descriptor_offset)
    NTAttribute.AddAlarm(builder, alarm_offset)
    NTAttribute.AddTime(builder, time_offset)
    NTAttribute.AddSourceType(builder, ntattribute_data.sourceType)
    NTAttribute.AddSource(builder, source_offset)
    return NTAttribute.End(builder)


@safe_deserialise
def deserialise_ntattribute(buffer: NTAttribute.NTAttribute) -> dt.NTAttribute:
    """Deserialises the NTAttribute table from a FlatBuffer.

    Args:
        buffer: FlatBuffer object containing the serialised NTAttribute table.

    Returns:
        The deserialised Python object representation of the NTAttribute data.
    """
    return dt.NTAttribute(
        name=buffer.Name().decode("utf-8"),  # type: ignore
        value=deserialise_any(buffer.Value()),
        tags=[buffer.Tags(i).decode("utf-8") for i in range(buffer.TagsLength())],
        descriptor=buffer.Descriptor().decode("utf-8"),  # type: ignore
        alarm=deserialise_alarm(buffer.Alarm()),
        time=deserialise_time(buffer.Time()),
        sourceType=buffer.SourceType(),
        source=buffer.Source().decode("utf-8"),  # type: ignore
    )


@safe_serialise
def serialise_column(builder: flatbuffers.Builder, column_data: dt.Column) -> int:
    """serialises a Column table into FlatBuffers format.

    Args:
        builder (flatbuffers.Builder): The FlatBuffers builder used to construct the object.
        column_data (dt.Column): The Column object containing column data.

    Returns:
        The FlatBuffers offset for the serialised Column object.
    """
    value_offset = serialise_any(builder, column_data.value)
    Column.Start(builder)
    Column.AddValue(builder, value_offset)
    return Column.End(builder)


@safe_deserialise
def deserialise_column(buffer: Column.Column) -> dt.Column:
    """Deserialises the Column table from a FlatBuffer.

    Args:
        buffer: FlatBuffer object containing the serialised Column table.

    Returns:
        The deserialised Python object representation of the Column data.
    """
    return dt.Column(value=deserialise_any(buffer.Value()))


def serialise_ntscalarany(
    builder: flatbuffers.Builder, ntscalarany_data: dt.NTScalarAny
) -> int:
    """serialises an NTScalarAny table into FlatBuffers format.

    Args:
        builder (flatbuffers.Builder): The FlatBuffers builder used to construct the object.
        ntscalarany_data (dt.NTScalarAny): The NTScalarAny object containing scalar details.

    Returns:
        The FlatBuffers offset for the serialised NTScalarAny object.
    """

    value_offset = serialise_any(builder, ntscalarany_data.value)
    descriptor_offset = builder.CreateString(ntscalarany_data.descriptor)
    alarm_offset = serialise_alarm(builder, ntscalarany_data.alarm)
    time_stamp_offset = serialise_time(builder, ntscalarany_data.timeStamp)
    display_offset = serialise_display(builder, ntscalarany_data.display)
    control_offset = serialise_control(builder, ntscalarany_data.control)

    # Create NTScalarAny
    NTScalarAny.Start(builder)
    NTScalarAny.AddValue(builder, value_offset)
    NTScalarAny.AddDescriptor(builder, descriptor_offset)
    NTScalarAny.AddAlarm(builder, alarm_offset)
    NTScalarAny.AddTimeStamp(builder, time_stamp_offset)
    NTScalarAny.AddDisplay(builder, display_offset)
    NTScalarAny.AddControl(builder, control_offset)
    return NTScalarAny.End(builder)


def deserialise_ntscalarany(buffer: NTScalarAny.NTScalarAny) -> dt.NTScalarAny:
    """Deserialises the NTScalarAny table from a FlatBuffer.

    Args:
        buffer: FlatBuffer object containing the serialised NTScalarAny table.

    Returns:
        The deserialised Python object representation of the NTScalarAny data.
    """
    return dt.NTScalarAny(
        value=deserialise_any(buffer.Value()),
        alarm=deserialise_alarm(buffer.Alarm()),
        timeStamp=deserialise_time(buffer.TimeStamp()),
        display=deserialise_display(buffer.Display()),
        control=deserialise_control(buffer.Control()),
    )


def serialise_ntndarray(
    builder: flatbuffers.Builder, ntndarray_data: dt.NTNDArray
) -> int:
    """serialises an NTNDArray table into FlatBuffers format.

    Args:
        builder (flatbuffers.Builder): The FlatBuffers builder used to construct the object.
        ntndarray_data (dt.NTNDArray): The NTNDArray object containing array data.

    Returns:
        The FlatBuffers offset for the serialised NTNDArray object.
    """

    value_offset = serialise_any(builder, ntndarray_data.value)
    codec_offset = serialise_codec(builder, ntndarray_data.codec)
    if ntndarray_data.dimension:
        dimensions_offsets = [
            serialise_dimension(builder, dimension)
            for dimension in ntndarray_data.dimension
        ]
        NTNDArray.StartDimensionVector(builder, len(dimensions_offsets))
        for offset in reversed(dimensions_offsets):
            builder.PrependUOffsetTRelative(offset)
        dimensions_vector_offset = builder.EndVector()
    else:
        dimensions_vector_offset = 0
    data_timestamp_offset = serialise_time(builder, ntndarray_data.dataTimeStamp)
    if ntndarray_data.attribute:
        attributes_offsets = [
            serialise_ntattribute(builder, attribute)
            for attribute in ntndarray_data.attribute
        ]
        NTNDArray.StartAttributeVector(builder, len(attributes_offsets))
        for offset in reversed(attributes_offsets):
            builder.PrependUOffsetTRelative(offset)
        attributes_vector_offset = builder.EndVector()
    else:
        attributes_vector_offset = 0
    descriptor_offset = builder.CreateString(ntndarray_data.descriptor)
    alarm_offset = serialise_alarm(builder, ntndarray_data.alarm)
    timestamp_offset = serialise_time(builder, ntndarray_data.timeStamp)
    display_offset = serialise_display(builder, ntndarray_data.display)

    # Build NTNDArray
    NTNDArray.Start(builder)
    NTNDArray.AddValue(builder, value_offset)
    NTNDArray.AddCodec(builder, codec_offset)
    NTNDArray.AddCompressedSize(builder, ntndarray_data.compressedSize)
    NTNDArray.AddUncompressedSize(builder, ntndarray_data.uncompressedSize)
    NTNDArray.AddDimension(builder, dimensions_vector_offset)
    NTNDArray.AddUniqueId(builder, ntndarray_data.uniqueId)
    NTNDArray.AddDataTimeStamp(builder, data_timestamp_offset)
    NTNDArray.AddAttribute(builder, attributes_vector_offset)
    NTNDArray.AddDescriptor(builder, descriptor_offset)
    NTNDArray.AddAlarm(builder, alarm_offset)
    NTNDArray.AddTimeStamp(builder, timestamp_offset)
    NTNDArray.AddDisplay(builder, display_offset)
    return NTNDArray.End(builder)


def deserialise_ntndarray(buffer: NTNDArray.NTNDArray) -> dt.NTNDArray:
    """Deserialises the NTNDArray table from a FlatBuffer.

    Args:
        buffer: FlatBuffer object containing the serialised NTNDArray table.

    Returns:
        The deserialised Python object representation of the NTNDArray data.
    """
    return dt.NTNDArray(
        value=deserialise_any(buffer.Value()),
        codec=deserialise_codec(buffer.Codec()),
        compressedSize=buffer.CompressedSize(),
        uncompressedSize=buffer.UncompressedSize(),
        dimension=[
            dim
            for i in range(buffer.DimensionLength())
            if (dim := deserialise_dimension(buffer.Dimension(i))) is not None
        ],
        uniqueId=buffer.UniqueId(),
        dataTimeStamp=(deserialise_time(buffer.DataTimeStamp())),
        attribute=[
            attr
            for i in range(buffer.AttributeLength())
            if (attr := deserialise_ntattribute(buffer.Attribute(i))) is not None
        ],
        descriptor=buffer.Descriptor().decode("utf-8"),  # type: ignore
        alarm=deserialise_alarm(buffer.Alarm()),
        timeStamp=deserialise_time(buffer.TimeStamp()),
        display=deserialise_display(buffer.Display()),
    )


def serialise_nttable(builder: flatbuffers.Builder, nttable_data: dt.NTTable) -> int:
    """serialises an NTTable table into FlatBuffers format.

    Args:
        builder (flatbuffers.Builder): The FlatBuffers builder used to construct the object.
        nttable_data (dt.NTTable): The NTTable object containing table data.

    Returns:
        The FlatBuffers offset for the serialised NTTable object.
    """
    labels_offsets = [builder.CreateString(label) for label in nttable_data.labels]
    NTTable.StartLabelsVector(builder, len(labels_offsets))
    for label_offset in reversed(labels_offsets):
        builder.PrependUOffsetTRelative(label_offset)
    labels_vector_offset = builder.EndVector()
    if nttable_data.value:
        column_offsets = [
            serialise_column(builder, column) for column in nttable_data.value
        ]
        NTTable.StartValueVector(builder, len(column_offsets))
        for offset in reversed(column_offsets):
            builder.PrependUOffsetTRelative(offset)
        value_vector_offset = builder.EndVector()
    else:
        value_vector_offset = 0
    descriptor_offset = builder.CreateString(nttable_data.descriptor)
    alarm_offset = serialise_alarm(builder, nttable_data.alarm)
    time_stamp_offset = serialise_time(builder, nttable_data.timeStamp)
    display_offset = serialise_display(builder, nttable_data.display)

    # Create NTScalarAny
    NTTable.Start(builder)
    NTTable.AddLabels(builder, labels_vector_offset)
    NTTable.NTTableAddValue(builder, value_vector_offset)
    NTTable.AddDescriptor(builder, descriptor_offset)
    NTTable.AddAlarm(builder, alarm_offset)
    NTTable.AddTimeStamp(builder, time_stamp_offset)
    NTTable.AddDisplay(builder, display_offset)
    return NTTable.End(builder)


def deserialise_nttable(buffer: NTTable.NTTable) -> dt.NTTable:
    """Deserialises the NTTable table from a FlatBuffer.

    Args:
        buffer: FlatBuffer object containing the serialised NTTable table.

    Returns:
        The deserialised Python object representation of the NTTable data.
    """
    return dt.NTTable(
        labels=[buffer.Labels(i).decode("utf-8") for i in range(buffer.LabelsLength())],
        value=[
            col
            for i in range(buffer.ValueLength())
            if (col := deserialise_column(buffer.Value(i))) is not None
        ],
        descriptor=buffer.Descriptor().decode("utf-8"),  # type: ignore
        alarm=deserialise_alarm(buffer.Alarm()),
        timeStamp=deserialise_time(buffer.TimeStamp()),
        display=deserialise_display(buffer.Display()),
    )


def serialise_data(data: dt.PVData) -> bytes:
    """serialises data into a FlatBuffer using PVData as the container type.

    Args:
        pv_name (str): The process variable (PV) name associated with the data.
        data_type (str): The type of data being serialised (e.g., "NTScalarAny", "NTNDArray", "NTTable").
        data (dt.PVData): The PVData object containing the data to serialise.

    Returns:
        The serialised FlatBuffer as a byte array.

    Raises:
        ValueError: If an unsupported or unknown data type is provided.
    """
    builder = flatbuffers.Builder(1024)

    if isinstance(data.data, dt.NTScalarAny):
        data_offset = serialise_ntscalarany(builder, data.data)
        data_enum = PVType.PVType.NTScalarAny
    elif isinstance(data.data, dt.NTNDArray):
        data_offset = serialise_ntndarray(builder, data.data)
        data_enum = PVType.PVType.NTNDArray
    elif isinstance(data.data, dt.NTTable):
        data_offset = serialise_nttable(builder, data.data)
        data_enum = PVType.PVType.NTTable
    else:
        raise TypeError(f"Unsupported data type: {type(data.data)}")

    pv_name_offset = builder.CreateString(data.pv_name)

    PVData.Start(builder)
    PVData.AddDataType(builder, data_enum)
    PVData.AddData(builder, data_offset)
    PVData.AddPvName(builder, pv_name_offset)
    pv_offset = PVData.End(builder)
    builder.Finish(pv_offset, file_identifier=FILE_IDENTIFIER)
    return bytes(builder.Output())


def deserialise_data(buffer: bytes) -> dt.PVData:
    """Deserialises FlatBuffer bytes containing PVData and dynamically handles
    various data types like NTScalarAny, NTNDArray, and NTTable.

    Args:
        buffer: FlatBuffer bytes containing PVData data.

    Returns:
        The deserialised Python object representation of the contained data type.

    Raises:
        ValueError: If an unsupported or unknown data type is encountered.
    """
    pv_data = PVData.PVData.GetRootAsPVData(buffer, 0)

    data_buffer = pv_data.Data()
    data_type = pv_data.DataType()

    if data_type == PVType.PVType.NTScalarAny:
        ntscalarany_data = NTScalarAny.NTScalarAny()
        ntscalarany_data.Init(data_buffer.Bytes, data_buffer.Pos)
        return dt.PVData(
            data=deserialise_ntscalarany(ntscalarany_data),
            pv_name=pv_data.PvName().decode("utf-8"),
        )
    elif data_type == PVType.PVType.NTNDArray:
        ntndarray_data = NTNDArray.NTNDArray()
        ntndarray_data.Init(data_buffer.Bytes, data_buffer.Pos)
        return dt.PVData(
            data=deserialise_ntndarray(ntndarray_data),
            pv_name=pv_data.PvName().decode("utf-8"),
        )
    elif data_type == PVType.PVType.NTTable:
        nttable_data = NTTable.NTTable()
        nttable_data.Init(data_buffer.Bytes, data_buffer.Pos)
        return dt.PVData(
            data=deserialise_nttable(nttable_data),
            pv_name=pv_data.PvName().decode("utf-8"),
        )
    else:
        raise ValueError(f"Unsupported data type: {data_type}")
