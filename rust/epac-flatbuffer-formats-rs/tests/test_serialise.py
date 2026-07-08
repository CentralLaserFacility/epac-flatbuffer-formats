# tests/test_serialise.py
import epac_flatbuffer_formats_rs as m
import numpy as np
import pytest

from epac.flatbuffers.fbschemas.pva0 import AlarmT as PyAlarmT
from epac.flatbuffers.fbschemas.pva0 import AnyT as PyAnyT
from epac.flatbuffers.fbschemas.pva0 import Bool as PyBool
from epac.flatbuffers.fbschemas.pva0 import Byte as PyByte
from epac.flatbuffers.fbschemas.pva0 import ControlT as PyControlT
from epac.flatbuffers.fbschemas.pva0 import DisplayT as PyDisplayT
from epac.flatbuffers.fbschemas.pva0 import Double as PyDouble
from epac.flatbuffers.fbschemas.pva0 import Float as PyFloat
from epac.flatbuffers.fbschemas.pva0 import Int as PyInt
from epac.flatbuffers.fbschemas.pva0 import Long as PyLong
from epac.flatbuffers.fbschemas.pva0 import NTScalarAny as PyNTScalarAny
from epac.flatbuffers.fbschemas.pva0 import Short as PyShort
from epac.flatbuffers.fbschemas.pva0 import String as PyString
from epac.flatbuffers.fbschemas.pva0 import TimeT as PyTimeT
from epac.flatbuffers.fbschemas.pva0 import UByte as PyUByte
from epac.flatbuffers.fbschemas.pva0 import UInt as PyUInt
from epac.flatbuffers.fbschemas.pva0 import ULong as PyULong
from epac.flatbuffers.fbschemas.pva0 import UShort as PyUShort
from epac.flatbuffers.fbschemas.pva0 import AnyInner as PyAnyInner
from epac.flatbuffers.fbschemas.pva0 import IntArray as PyIntArray


class FakeTimeT:
    secondsPastEpoch = 1234567890
    nanoseconds = 42
    userTag = 7


class FakeAlarmT:
    severity = 1  # MINOR
    status = 2  # RECORD
    message = "test alarm"


class FakeDisplayT:
    limitLow = -10.0
    limitHigh = 10.0
    description = "a display"
    units = "volts"
    precision = 3
    form = 2  # some DisplayForm value


class FakeControlT:
    limitLow = -5.0
    limitHigh = 5.0
    minStep = 0.1


class FakeNTScalarAny:
    value = np.float64(3.14159)
    descriptor = "a test scalar"
    alarm = FakeAlarmT()
    timeStamp = FakeTimeT()
    display = FakeDisplayT()
    control = FakeControlT()


def test_flatbuffer_roundtrip_check():
    assert m.flatbuffer_roundtrip_check() is True


def test_serialise_any_array():
    result = m.serialise_any_array(np.array([1, -2, 3, 2147483647], dtype=np.int32))

    any_t = PyAnyT.AnyT.GetRootAsAnyT(result, 0)
    assert any_t.ValueType() == PyAnyInner.AnyInner.IntArray

    inner = PyIntArray.IntArray()
    inner.Init(any_t.Value().Bytes, any_t.Value().Pos)
    assert inner.ValueAsNumpy().tolist() == [1, -2, 3, 2147483647]


@pytest.mark.parametrize(
    "value, expected_variant, py_type, expected_value",
    [
        (np.bool_(True), PyAnyInner.AnyInner.Bool, PyBool.Bool, True),
        (np.int8(-12), PyAnyInner.AnyInner.Byte, PyByte.Byte, -12),
        (np.uint8(200), PyAnyInner.AnyInner.UByte, PyUByte.UByte, 200),
        (np.int16(-1234), PyAnyInner.AnyInner.Short, PyShort.Short, -1234),
        (np.uint16(60000), PyAnyInner.AnyInner.UShort, PyUShort.UShort, 60000),
        (np.int32(42), PyAnyInner.AnyInner.Int, PyInt.Int, 42),
        (np.uint32(4000000000), PyAnyInner.AnyInner.UInt, PyUInt.UInt, 4000000000),
        (np.int64(1234567890123), PyAnyInner.AnyInner.Long, PyLong.Long, 1234567890123),
        (
            np.uint64(18000000000000000000),
            PyAnyInner.AnyInner.ULong,
            PyULong.ULong,
            18000000000000000000,
        ),
        (np.float32(1.5), PyAnyInner.AnyInner.Float, PyFloat.Float, pytest.approx(1.5)),
        (
            np.float64(3.14159),
            PyAnyInner.AnyInner.Double,
            PyDouble.Double,
            pytest.approx(3.14159),
        ),
    ],
)
def test_serialise_any_scalar(value, expected_variant, py_type, expected_value):
    result = m.serialise_any(value)
    any_t = PyAnyT.AnyT.GetRootAsAnyT(result, 0)
    assert any_t.ValueType() == expected_variant

    inner = py_type()
    inner.Init(any_t.Value().Bytes, any_t.Value().Pos)
    assert inner.Value() == expected_value


def test_serialise_any_string():
    result = m.serialise_any(np.str_("hello world"))
    any_t = PyAnyT.AnyT.GetRootAsAnyT(result, 0)
    assert any_t.ValueType() == PyAnyInner.AnyInner.String

    inner = PyString.String()
    inner.Init(any_t.Value().Bytes, any_t.Value().Pos)
    assert inner.Value().decode("utf-8") == "hello world"


def test_serialise_time():
    result = m.serialise_time(FakeTimeT())
    parsed = PyTimeT.TimeT.GetRootAsTimeT(result, 0)
    assert parsed.SecondsPastEpoch() == 1234567890
    assert parsed.Nanoseconds() == 42
    assert parsed.UserTag() == 7


def test_serialise_alarm():
    result = m.serialise_alarm(FakeAlarmT())
    parsed = PyAlarmT.AlarmT.GetRootAsAlarmT(result, 0)
    assert parsed.Severity() == 1
    assert parsed.Status() == 2
    assert parsed.Message().decode("utf-8") == "test alarm"


def test_serialise_display():
    result = m.serialise_display(FakeDisplayT())
    parsed = PyDisplayT.DisplayT.GetRootAsDisplayT(result, 0)
    assert parsed.LimitLow() == -10.0
    assert parsed.LimitHigh() == 10.0
    assert parsed.Description().decode("utf-8") == "a display"
    assert parsed.Units().decode("utf-8") == "volts"
    assert parsed.Precision() == 3
    assert parsed.Form() == 2


def test_serialise_control():
    result = m.serialise_control(FakeControlT())
    parsed = PyControlT.ControlT.GetRootAsControlT(result, 0)
    assert parsed.LimitLow() == -5.0
    assert parsed.LimitHigh() == 5.0
    assert parsed.MinStep() == 0.1


def test_serialise_ntscalarany():
    result = m.serialise_ntscalarany(FakeNTScalarAny())
    parsed = PyNTScalarAny.NTScalarAny.GetRootAsNTScalarAny(result, 0)

    assert parsed.Descriptor().decode("utf-8") == "a test scalar"

    assert parsed.Alarm().Severity() == 1
    assert parsed.Alarm().Status() == 2
    assert parsed.Alarm().Message().decode("utf-8") == "test alarm"

    assert parsed.TimeStamp().SecondsPastEpoch() == 1234567890
    assert parsed.TimeStamp().Nanoseconds() == 42
    assert parsed.TimeStamp().UserTag() == 7

    any_value = parsed.Value()
    assert any_value.ValueType() == PyAnyInner.AnyInner.Double
    double_table = PyDouble.Double()
    double_table.Init(any_value.Value().Bytes, any_value.Value().Pos)
    assert double_table.Value() == pytest.approx(3.14159)

    display = parsed.Display()
    assert display.LimitLow() == -10.0
    assert display.LimitHigh() == 10.0
    assert display.Description().decode("utf-8") == "a display"
    assert display.Units().decode("utf-8") == "volts"
    assert display.Precision() == 3
    assert display.Form() == 2

    control = parsed.Control()
    assert control.LimitLow() == -5.0
    assert control.LimitHigh() == 5.0
    assert control.MinStep() == 0.1
