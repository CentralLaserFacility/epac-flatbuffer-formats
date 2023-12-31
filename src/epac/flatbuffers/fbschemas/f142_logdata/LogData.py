# automatically generated by the FlatBuffers compiler, do not modify

# namespace:

import flatbuffers
from flatbuffers.compat import import_numpy
from typing import Any
from flatbuffers.table import Table
from typing import Optional

np = import_numpy()


class LogData(object):
    __slots__ = ["_tab"]

    @classmethod
    def GetRootAs(cls, buf, offset: int = 0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = LogData()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsLogData(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)

    @classmethod
    def LogDataBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(
            buf, offset, b"\x66\x31\x34\x32", size_prefixed=size_prefixed
        )

    # LogData
    def Init(self, buf: bytes, pos: int):
        self._tab = flatbuffers.table.Table(buf, pos)

    # LogData
    def SourceName(self) -> Optional[str]:
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # LogData
    def ValueType(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, o + self._tab.Pos)
        return 0

    # LogData
    def Value(self) -> Optional[flatbuffers.table.Table]:
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            obj = Table(bytearray(), 0)
            self._tab.Union(obj, o)
            return obj
        return None

    # LogData
    def Timestamp(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.Get(
                flatbuffers.number_types.Uint64Flags, o + self._tab.Pos
            )
        return 0

    # LogData
    def Status(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return self._tab.Get(
                flatbuffers.number_types.Uint16Flags, o + self._tab.Pos
            )
        return 22

    # LogData
    def Severity(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            return self._tab.Get(
                flatbuffers.number_types.Uint16Flags, o + self._tab.Pos
            )
        return 4


def LogDataStart(builder: flatbuffers.Builder):
    builder.StartObject(6)


def Start(builder: flatbuffers.Builder):
    LogDataStart(builder)


def LogDataAddSourceName(builder: flatbuffers.Builder, sourceName: int):
    builder.PrependUOffsetTRelativeSlot(
        0, flatbuffers.number_types.UOffsetTFlags.py_type(sourceName), 0
    )


def AddSourceName(builder: flatbuffers.Builder, sourceName: int):
    LogDataAddSourceName(builder, sourceName)


def LogDataAddValueType(builder: flatbuffers.Builder, valueType: int):
    builder.PrependUint8Slot(1, valueType, 0)


def AddValueType(builder: flatbuffers.Builder, valueType: int):
    LogDataAddValueType(builder, valueType)


def LogDataAddValue(builder: flatbuffers.Builder, value: int):
    builder.PrependUOffsetTRelativeSlot(
        2, flatbuffers.number_types.UOffsetTFlags.py_type(value), 0
    )


def AddValue(builder: flatbuffers.Builder, value: int):
    LogDataAddValue(builder, value)


def LogDataAddTimestamp(builder: flatbuffers.Builder, timestamp: int):
    builder.PrependUint64Slot(3, timestamp, 0)


def AddTimestamp(builder: flatbuffers.Builder, timestamp: int):
    LogDataAddTimestamp(builder, timestamp)


def LogDataAddStatus(builder: flatbuffers.Builder, status: int):
    builder.PrependUint16Slot(4, status, 22)


def AddStatus(builder: flatbuffers.Builder, status: int):
    LogDataAddStatus(builder, status)


def LogDataAddSeverity(builder: flatbuffers.Builder, severity: int):
    builder.PrependUint16Slot(5, severity, 4)


def AddSeverity(builder: flatbuffers.Builder, severity: int):
    LogDataAddSeverity(builder, severity)


def LogDataEnd(builder: flatbuffers.Builder) -> int:
    return builder.EndObject()


def End(builder: flatbuffers.Builder) -> int:
    return LogDataEnd(builder)
