# automatically generated by the FlatBuffers compiler, do not modify

# namespace:

import flatbuffers
from flatbuffers.compat import import_numpy
from typing import Any

np = import_numpy()


class ULong(object):
    __slots__ = ["_tab"]

    @classmethod
    def GetRootAs(cls, buf, offset: int = 0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = ULong()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsULong(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)

    @classmethod
    def ULongBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(
            buf, offset, b"\x66\x31\x34\x32", size_prefixed=size_prefixed
        )

    # ULong
    def Init(self, buf: bytes, pos: int):
        self._tab = flatbuffers.table.Table(buf, pos)

    # ULong
    def Value(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(
                flatbuffers.number_types.Uint64Flags, o + self._tab.Pos
            )
        return 0


def ULongStart(builder: flatbuffers.Builder):
    builder.StartObject(1)


def Start(builder: flatbuffers.Builder):
    ULongStart(builder)


def ULongAddValue(builder: flatbuffers.Builder, value: int):
    builder.PrependUint64Slot(0, value, 0)


def AddValue(builder: flatbuffers.Builder, value: int):
    ULongAddValue(builder, value)


def ULongEnd(builder: flatbuffers.Builder) -> int:
    return builder.EndObject()


def End(builder: flatbuffers.Builder) -> int:
    return ULongEnd(builder)
