# automatically generated by the FlatBuffers compiler, do not modify

# namespace:

import flatbuffers
from flatbuffers.compat import import_numpy

np = import_numpy()


class Float(object):
    __slots__ = ["_tab"]

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Float()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsFloat(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)

    @classmethod
    def FloatBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(
            buf, offset, b"\x66\x31\x34\x32", size_prefixed=size_prefixed
        )

    # Float
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Float
    def Value(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(
                flatbuffers.number_types.Float32Flags, o + self._tab.Pos
            )
        return 0.0


def FloatStart(builder):
    builder.StartObject(1)


def Start(builder):
    FloatStart(builder)


def FloatAddValue(builder, value):
    builder.PrependFloat32Slot(0, value, 0.0)


def AddValue(builder, value):
    FloatAddValue(builder, value)


def FloatEnd(builder):
    return builder.EndObject()


def End(builder):
    return FloatEnd(builder)
