from typing import Annotated, Any, Optional, Union

from pydantic import BaseModel, BeforeValidator


class EnumT(BaseModel):
    index: int = 0
    choices: list[str] = []


def extract_enum(form: Optional[Any]) -> int:
    """Handles both EnumT-style input and direct string values."""
    if isinstance(form, dict):
        enum_obj = EnumT(**form)
        return enum_obj.index
    elif isinstance(form, int):
        return form
    return 0


class AlarmT(BaseModel):
    severity: int = 0
    status: int = 0
    message: str = ""


class TimeT(BaseModel):
    secondsPastEpoch: int = 0
    nanoseconds: int = 0
    userTag: int = 0


class DisplayT(BaseModel):
    limitLow: float = 0
    limitHigh: float = 0
    description: str = ""
    units: str = ""
    precision: int = 0
    form: Annotated[int, BeforeValidator(extract_enum)] = 0


class ControlT(BaseModel):
    limitLow: float = 0
    limitHigh: float = 0
    minStep: float = 0


class CodecT(BaseModel):
    name: str = ""
    parameters: Any


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
    value: Any
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
    value: Any
    descriptor: str = ""
    alarm: Optional[AlarmT] = None
    timeStamp: Optional[TimeT] = None
    display: Optional[DisplayT] = None
    control: Optional[ControlT] = None


class Column(BaseModel):
    value: Any


class NTTable(BaseModel):
    labels: list[str] = []
    value: list[Column] = []
    descriptor: str = ""
    alarm: Optional[AlarmT] = None
    timeStamp: Optional[TimeT] = None
    display: Optional[DisplayT] = None


class CAScalarAny(BaseModel):
    value: Any
    pvname: str = ""
    status: int = 0
    precision: Optional[int] = (
        0  # precision appears to be the only optional field in pyepics (form="ctrl")
    )
    units: str = ""
    severity: int = 0
    timestamp: float
    upper_disp_limit: float = 0
    lower_disp_limit: float = 0
    upper_ctrl_limit: float = 0
    lower_ctrl_limit: float = 0


class PVData(BaseModel):
    data: Union[NTScalarAny, NTNDArray, NTTable, CAScalarAny]
    pv_name: str = ""
