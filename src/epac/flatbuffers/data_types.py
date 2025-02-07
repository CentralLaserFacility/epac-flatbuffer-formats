from pydantic import BaseModel
from typing import Any, Optional, Union


class EnumT(BaseModel):
    index: int = 0
    choices: list[str] = []


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
    form: Optional[EnumT] = None


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


class NTScalarAll(BaseModel):
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


class PVData(BaseModel):
    data: Union[NTScalarAll, NTNDArray, NTTable]
    pv_name: str = ""
