# automatically generated by the FlatBuffers compiler, do not modify

# namespace:

import flatbuffers
from flatbuffers.compat import import_numpy

np = import_numpy()


class ArrayFloat(object):
    __slots__ = ["_tab"]

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = ArrayFloat()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsArrayFloat(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)

    @classmethod
    def ArrayFloatBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(
            buf, offset, b"\x66\x31\x34\x32", size_prefixed=size_prefixed
        )

    # ArrayFloat
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # ArrayFloat
    def Value(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(
                flatbuffers.number_types.Float32Flags,
                a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 4),
            )
        return 0

    # ArrayFloat
    def ValueAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Float32Flags, o)
        return 0

    # ArrayFloat
    def ValueLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # ArrayFloat
    def ValueIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        return o == 0


def ArrayFloatStart(builder):
    builder.StartObject(1)


def Start(builder):
    ArrayFloatStart(builder)


def ArrayFloatAddValue(builder, value):
    builder.PrependUOffsetTRelativeSlot(
        0, flatbuffers.number_types.UOffsetTFlags.py_type(value), 0
    )


def AddValue(builder, value):
    ArrayFloatAddValue(builder, value)


def ArrayFloatStartValueVector(builder, numElems):
    return builder.StartVector(4, numElems, 4)


def StartValueVector(builder, numElems: int) -> int:
    return ArrayFloatStartValueVector(builder, numElems)


def ArrayFloatEnd(builder):
    return builder.EndObject()


def End(builder):
    return ArrayFloatEnd(builder)
