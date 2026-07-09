import numpy as np
import pytest
from epac_flatbuffer_formats_rs import (  # type: ignore
    serialise_nt_scalar_any,
    serialise_pv_data,
)

from epac.flatbuffers.data_types import (
    AlarmT,
    ControlT,
    DisplayT,
    NTScalarAny,
    PVData,
    TimeT,
)
from epac.flatbuffers.pva0_data import deserialise_data


@pytest.fixture
def fake_time():
    return TimeT(
        secondsPastEpoch=1234567890,
        nanoseconds=42,
        userTag=7,
    )


@pytest.fixture
def fake_alarm():
    return AlarmT(
        severity=1,  # MINOR
        status=2,  # RECORD
        message="test alarm",
    )


@pytest.fixture
def fake_display():
    return DisplayT(
        limitLow=-10.0,
        limitHigh=10.0,
        description="Display",
        units="volts",
        precision=3,
        form=2,  # some DisplayForm Value
    )


@pytest.fixture
def fake_control():
    return ControlT(
        limitLow=-5.0,
        limitHigh=5.0,
        minStep=0.1,
    )


@pytest.fixture
def fake_nt_scalar_any(
    fake_alarm,
    fake_time,
    fake_display,
    fake_control,
):
    return NTScalarAny(
        value=np.float64(3.14159),
        descriptor="a test scalar",
        alarm=fake_alarm,
        timeStamp=fake_time,
        display=fake_display,
        control=fake_control,
    )


@pytest.fixture
def fake_pv_data(fake_nt_scalar_any):
    return PVData(
        data=fake_nt_scalar_any,
        sourceName="Timbuktu",
    )


def test_serialise_nt_scalar_any_from_python_object(fake_nt_scalar_any):
    payload = serialise_nt_scalar_any(fake_nt_scalar_any)
    assert isinstance(payload, bytes)
    assert len(payload) > 0


def test_serialise_pv_data_from_python_object(fake_pv_data):
    payload = serialise_pv_data(fake_pv_data)
    assert isinstance(payload, bytes)
    assert len(payload) > 0


def test_round_trip(fake_pv_data) -> None:
    # serialise (with rust)
    payload = serialise_pv_data(fake_pv_data)
    assert len(payload) > 0

    # deserialise (with python) and compare
    unpacked = deserialise_data(payload)
    assert isinstance(unpacked, PVData)

    unpacked_dict: dict = unpacked.model_dump()
    raw_dict: dict = fake_pv_data.model_dump()
    for key in unpacked_dict.keys():
        assert unpacked_dict.get(key) == raw_dict.get(key)
