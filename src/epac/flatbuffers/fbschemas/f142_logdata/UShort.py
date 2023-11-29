# automatically generated by the FlatBuffers compiler, do not modify

# namespace:

import flatbuffers
from flatbuffers.compat import import_numpy
from typing import Any

np = import_numpy()


class UShort(object):
    __slots__ = ["_tab"]

    @classmethod
    def GetRootAs(cls, buf, offset: int = 0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = UShort()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsUShort(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)

    @classmethod
    def UShortBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(
            buf, offset, b"\x66\x31\x34\x32", size_prefixed=size_prefixed
        )

    # UShort
    def Init(self, buf: bytes, pos: int):
        self._tab = flatbuffers.table.Table(buf, pos)

    # UShort
    def Value(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(
                flatbuffers.number_types.Uint16Flags, o + self._tab.Pos
            )
        return 0


def UShortStart(builder: flatbuffers.Builder):
    builder.StartObject(1)


def Start(builder: flatbuffers.Builder):
    UShortStart(builder)


def UShortAddValue(builder: flatbuffers.Builder, value: int):
    builder.PrependUint16Slot(0, value, 0)


def AddValue(builder: flatbuffers.Builder, value: int):
    UShortAddValue(builder, value)


def UShortEnd(builder: flatbuffers.Builder) -> int:
    return builder.EndObject()


def End(builder: flatbuffers.Builder) -> int:
    return UShortEnd(builder)
