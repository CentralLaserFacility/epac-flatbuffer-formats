from functools import partial
from typing import Annotated, Any, Optional, Tuple, Union

from pydantic import BaseModel, BeforeValidator

from epac.flatbuffers.fbschemas.pva0.AlarmSeverity import AlarmSeverity
from epac.flatbuffers.fbschemas.pva0.AlarmStatus import AlarmStatus
from epac.flatbuffers.fbschemas.pva0.DisplayForm import DisplayForm


class EnumT(BaseModel):
    index: int = 0
    choices: list[str] = []


def required():
    """Returns a BeforeValidator that raises an error if the field is None."""

    def _validate(v):
        if v is None:
            raise ValueError("value is missing")
        return v

    return BeforeValidator(_validate)


def replace_none(default_value):
    """Returns a validator that replaces None with a given default value."""
    return BeforeValidator(lambda v: v if v is not None else default_value)


def extract_enum(enum_value: Optional[Any], enum_name: str, enum_type) -> int:
    """Handles both EnumT-style input and direct integer values, ensuring validity against enum_type."""

    if not enum_value:
        return 0

    if isinstance(enum_value, dict):
        enum_obj = EnumT(**enum_value)
        enum_value = enum_obj.index  # Extract index

    if not isinstance(enum_value, int):
        raise TypeError(f"invalid data type provided to {enum_name}")

    # TODO optimise this step
    if enum_value not in vars(enum_type).values():
        raise ValueError(f"invalid value {enum_value} provided to {enum_name}")

    return enum_value


def parse_enum(enum_name: str, enum_type):
    """Returns a BeforeValidator that validates and extracts enum values."""
    return BeforeValidator(
        partial(extract_enum, enum_name=enum_name, enum_type=enum_type)
    )


RequiredAny = Annotated[Any, required()]


class AlarmT(BaseModel):
    severity: Annotated[
        int, parse_enum(enum_name="Alarm Severity", enum_type=AlarmSeverity)
    ] = 0
    status: Annotated[
        int, parse_enum(enum_name="Alarm Status", enum_type=AlarmStatus)
    ] = 0
    message: str = ""


class TimeT(BaseModel):
    secondsPastEpoch: int = 0
    nanoseconds: int = 0
    userTag: int = 0

    @staticmethod
    def float_to_time_components(timestamp: float) -> Tuple[int, int]:
        """Convert float seconds -> (seconds, nanoseconds)"""
        seconds = int(timestamp)
        nanoseconds = int((timestamp - seconds) * 1e9)
        return seconds, nanoseconds

    def __sub__(self, exposure_time: float) -> "TimeT":
        """Subtract exposure_time (float seconds)

        Args:
        - exposure_time: float seconds

        Returns: Self (TimeT)
        """
        if not isinstance(exposure_time, (int, float)):
            return NotImplemented

        if exposure_time < 0:
            raise ValueError("Exposure_time must be non-negative")

        # Convert exposure time
        exposure_time_s, exposure_time_ns = self.float_to_time_components(exposure_time)

        seconds = self.secondsPastEpoch
        nanoseconds = self.nanoseconds

        # Borrow if needed for nanoseconds subtraction
        if nanoseconds < exposure_time_ns:
            nanoseconds += int(1e9)
            seconds -= 1

        return TimeT(
            secondsPastEpoch=seconds - exposure_time_s,
            nanoseconds=nanoseconds - exposure_time_ns,
            userTag=self.userTag,
        )


class DisplayT(BaseModel):
    limitLow: float = 0
    limitHigh: float = 0
    description: str = ""
    units: str = ""
    precision: int = 0
    form: Annotated[
        int, parse_enum(enum_name="Display Form", enum_type=DisplayForm)
    ] = 0


class ControlT(BaseModel):
    limitLow: float = 0
    limitHigh: float = 0
    minStep: float = 0


class CodecT(BaseModel):
    name: str = ""


class DimensionT(BaseModel):
    size: int = 0
    offset: int = 0
    fullSize: int = 0
    binning: int = 1
    reverse: bool = False


class NTAttribute(BaseModel):
    name: str = ""
    value: Any
    tags: list[str] = []
    descriptor: str = ""
    alarm: Optional[AlarmT] = None
    time: Optional[TimeT] = None
    sourceType: int = 0
    source: str = ""


class NTNDArray(BaseModel):
    value: RequiredAny
    codec: Optional[CodecT] = None
    compressedSize: int = 0
    uncompressedSize: int = 0
    dimension: list[DimensionT] = []
    uniqueId: int = 0
    dataTimeStamp: Optional[TimeT] = None
    attribute: list[NTAttribute] = []
    descriptor: str = ""
    alarm: Optional[AlarmT] = None
    timeStamp: Optional[TimeT] = None
    display: Optional[DisplayT] = None


class NTScalarAny(BaseModel):
    value: RequiredAny
    descriptor: str = ""
    alarm: Optional[AlarmT] = None
    timeStamp: Optional[TimeT] = None
    display: Optional[DisplayT] = None
    control: Optional[ControlT] = None


class Column(BaseModel):
    value: RequiredAny


class NTTable(BaseModel):
    labels: list[str] = []
    value: list[Column] = []
    descriptor: str = ""
    alarm: Optional[AlarmT] = None
    timeStamp: Optional[TimeT] = None
    display: Optional[DisplayT] = None


class XYData(BaseModel):
    x: NTScalarAny
    y: NTScalarAny


class CAScalarAny(BaseModel):
    value: RequiredAny
    pvname: Annotated[str, replace_none("")] = ""
    status: Annotated[int, replace_none(0)] = 0
    precision: Annotated[int, replace_none(0)] = 0
    units: Annotated[str, replace_none("")] = ""
    severity: Annotated[int, replace_none(0)] = 0
    timestamp: float
    upper_disp_limit: Annotated[float, replace_none(0.0)] = 0.0
    lower_disp_limit: Annotated[float, replace_none(0.0)] = 0.0
    upper_ctrl_limit: Annotated[float, replace_none(0.0)] = 0.0
    lower_ctrl_limit: Annotated[float, replace_none(0.0)] = 0.0


class PulseID(BaseModel):
    value: int = 0
    timestamp: float = 0.0


class PVData(BaseModel):
    data: Union[NTScalarAny, NTNDArray, NTTable, XYData]
    sourceName: str = ""
    pulseId: Optional[PulseID] = None
    effectiveTimeStamp: Optional[TimeT] = None
