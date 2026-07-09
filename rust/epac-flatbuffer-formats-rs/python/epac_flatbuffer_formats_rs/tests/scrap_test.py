import numpy as np
import pytest
from epac_flatbuffer_formats_rs import (  # type: ignore
    serialise_nt_scalar_any,
    serialise_pv_data,
)

from epac.flatbuffers.pva0_data import deserialise_data


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


class FakePVData:
    data = FakeNTScalarAny()
    sourceName = "Timbuktu"


@pytest.fixture
def pv_data():
    return FakePVData()


@pytest.fixture
def scalar_any():
    return FakeNTScalarAny()


def test_serialise_nt_scalar_any_from_python_object(scalar_any):
    payload = serialise_nt_scalar_any(scalar_any)
    assert isinstance(payload, bytes)
    assert len(payload) > 0


def test_serialise_pv_data_from_python_object(pv_data):
    payload = serialise_pv_data(pv_data)
    assert isinstance(payload, bytes)
    assert len(payload) > 0


def test_round_trip(pv_data):
    payload = serialise_pv_data(pv_data)

    unpacked = deserialise_data(payload)

    # TODO create better assertions here
    # probably need to directly instantiate a proper PVData object
    assert unpacked.sourceName == "Timbuktu"
