import importlib
import os
from typing import Literal

import numpy as np
import numpy.testing as npt
import pytest
from hypothesis import given
from hypothesis import strategies as st

from epac.flatbuffers.data_types import (
    AlarmT,
    CodecT,
    Column,
    ControlT,
    DimensionT,
    DisplayT,
    NTAttribute,
    NTNDArray,
    NTScalarAny,
    NTTable,
    PulseID,
    PVData,
    TimeT,
    XYData,
)
from epac.flatbuffers.pva0_data import deserialise_data
from epac.flatbuffers.pva0_data import serialise_data as python_serialise

# limits on value for i32 type
MAX_I32 = 2147483647
MIN_I32 = -2147483647
# limits on value for i64 type
MAX_I64 = 9223372036854775807
MIN_I64 = -9223372036854775807


def running_on_ci() -> bool:
    """Returns true if running on CI."""
    return os.environ.get("CI") is not None


# conditionally skip tests if `epac_flatbuffer_formats_rs` is not installed
bindings_installed = pytest.mark.skipif(
    not importlib.util.find_spec("epac_flatbuffer_formats_rs") and not running_on_ci(),
    reason="requires rust bindings to be installed",
)


def assert_equal_any(expected, actual) -> None:
    """Assert equal, including numpy arrays and nested dicts"""
    if isinstance(expected, np.ndarray):
        npt.assert_array_equal(expected, actual)

    elif isinstance(expected, dict) and isinstance(actual, dict):
        assert expected.keys() == actual.keys()
        for key in expected.keys():
            assert_equal_any(expected[key], actual[key])

    elif isinstance(expected, list) and isinstance(actual, list):
        for expected_item, actual_item in zip(expected, actual, strict=True):
            assert_equal_any(expected_item, actual_item)

    else:
        assert expected == actual


@st.composite
def mock_any_t(draw):
    scalars = [
        st.integers(min_value=MIN_I64, max_value=MAX_I64),
        st.booleans(),
        st.floats(
            allow_infinity=False,
            allow_nan=False,
        ),
        st.text(),
    ]
    arrays = [
        st.builds(np.array, st.lists(st.booleans())),
        st.builds(
            np.array, st.lists(st.integers(min_value=MIN_I64, max_value=MAX_I64))
        ),
        st.builds(
            np.array,
            st.lists(
                st.floats(
                    allow_infinity=False,
                    allow_nan=False,
                )
            ),
        ),
        st.builds(np.array, st.lists(st.text())),
    ]
    any_t = scalars + arrays

    return draw(st.one_of(any_t))


@st.composite
def mock_time(draw):
    return TimeT(
        secondsPastEpoch=draw(
            st.integers(
                min_value=1780315200,  # 1pm 1st June 2026
                max_value=4115534400,  # 1pm 1st June 2100
            )
        ),
        nanoseconds=draw(st.integers(min_value=0, max_value=1e9)),
        userTag=draw(st.integers(min_value=1, max_value=9)),
    )


@st.composite
def mock_alarm(draw):
    return AlarmT(
        severity=draw(st.integers(min_value=0, max_value=4)),  # allowed range is 0-4
        status=draw(st.integers(min_value=0, max_value=7)),  # allowed range is 0-7
        message=draw(st.text()),
    )


@st.composite
def mock_display(draw):
    limitLow = draw(st.floats(allow_nan=False, allow_infinity=False))
    return DisplayT(
        limitLow=limitLow,
        limitHigh=draw(
            st.floats(min_value=limitLow, allow_nan=False, allow_infinity=False)
        ),
        description=draw(st.text()),
        units=draw(st.text()),
        precision=draw(st.integers(0, 9)),
        form=draw(st.integers(0, 6)),  # allowed range is 0-6
    )


@st.composite
def mock_control(draw):
    limitLow = draw(st.floats(allow_nan=False, allow_infinity=False))
    return ControlT(
        limitLow=limitLow,
        limitHigh=draw(
            st.floats(min_value=limitLow, allow_nan=False, allow_infinity=False)
        ),
        minStep=draw(st.floats(0, 10, allow_nan=False, allow_infinity=False)),
    )


@st.composite
def mock_nt_scalar_any(draw):
    return NTScalarAny(
        value=draw(mock_any_t()),
        descriptor=draw(st.text()),
        alarm=draw(st.one_of(mock_alarm(), st.none())),
        timeStamp=draw(st.one_of(mock_time(), st.none())),
        display=draw(st.one_of(mock_display(), st.none())),
        control=draw(st.one_of(mock_control(), st.none())),
    )


@st.composite
def mock_dimension_t(draw):
    return DimensionT(  # all i32
        size=draw(st.integers(min_value=MIN_I32, max_value=MAX_I32)),
        offset=draw(st.integers(min_value=MIN_I32, max_value=MAX_I32)),
        fullSize=draw(st.integers(min_value=MIN_I32, max_value=MAX_I32)),
        binning=draw(st.integers(min_value=MIN_I32, max_value=MAX_I32)),
        reverse=draw(st.booleans()),
    )


@st.composite
def mock_codec(draw):
    return CodecT(name=draw(st.text()))


@st.composite
def mock_column(draw):
    return Column(value=draw(mock_any_t()))


@st.composite
def mock_nt_attribute(draw):
    return NTAttribute(
        name=draw(st.text()),
        value=draw(mock_any_t()),
        tags=draw(st.lists(st.text())),
        descriptor=draw(st.text()),
        alarm=draw(st.one_of(mock_alarm(), st.none())),
        time=draw(st.one_of(mock_time(), st.none())),
        sourceType=draw(st.integers(min_value=MIN_I32, max_value=MAX_I32)),
        source=draw(st.text()),
    )


@st.composite
def mock_nt_nd_array(draw):
    compressed_size = draw(st.integers(min_value=0, max_value=1048))
    return NTNDArray(
        value=draw(mock_any_t()),
        codec=draw(st.one_of(mock_codec(), st.none())),
        compressedSize=compressed_size,
        uncompressedSize=draw(st.integers(min_value=compressed_size, max_value=1048)),
        dimension=draw(st.lists(mock_dimension_t(), min_size=1, max_size=9)),
        uniqueId=draw(st.integers(min_value=MIN_I32, max_value=MAX_I32)),  # i32
        dataTimeStamp=draw(st.one_of(mock_time(), st.none())),
        attribute=draw(st.lists(mock_nt_attribute(), min_size=0, max_size=10)),
        descriptor=draw(st.text()),
        alarm=draw(st.one_of(mock_alarm(), st.none())),
        timeStamp=draw(st.one_of(mock_time(), st.none())),
        display=draw(st.one_of(mock_display(), st.none())),
    )


@st.composite
def mock_nt_table(draw):
    return NTTable(
        labels=draw(st.lists(st.text())),
        value=draw(st.lists(mock_column())),
        descriptor=draw(st.text()),
        alarm=draw(st.one_of(mock_alarm(), st.none())),
        timeStamp=draw(st.one_of(mock_time(), st.none())),
        display=draw(st.one_of(mock_display(), st.none())),
    )


@st.composite
def mock_xy_data(draw):
    return XYData(x=draw(mock_nt_scalar_any()), y=draw(mock_nt_scalar_any()))


@st.composite
def pulse_id(draw):
    return PulseID(
        value=draw(st.integers(min_value=1, max_value=MAX_I64)),
        timestamp=draw(st.floats(allow_infinity=False, allow_nan=False)),
    )


@st.composite
def mock_pv_data(draw):
    payload_types = [
        mock_nt_scalar_any(),
        mock_nt_nd_array(),
        mock_nt_table(),
        mock_xy_data(),
    ]
    return PVData(
        data=draw(st.one_of(payload_types)),
        sourceName=draw(st.text()),
        pulseId=draw(st.one_of(pulse_id(), st.none())),
    )


def _roundtrip(
    mock_pv_data: PVData, serialise_backend: Literal["python", "rust"] = "rust"
) -> None:
    """
    Serialise then deserialise with specified backend (default is rust).
    Then assert the roundtrip object is the same as the original.
    """
    from epac_flatbuffer_formats_rs import serialise_pv_data

    backend = serialise_backend.lower()
    if backend == "rust":
        # serialise with rust
        payload = serialise_pv_data(mock_pv_data)
    elif backend == "python":
        # serialise with python
        payload = python_serialise(mock_pv_data)
    else:
        raise ValueError(
            "Only 'rust' and 'python' argument accepted for the serialisation"
        )

    assert len(payload) > 0

    # deserialise (with python)
    unpacked = deserialise_data(payload)
    assert isinstance(unpacked, PVData)

    unpacked_dict: dict = unpacked.model_dump()
    raw_dict: dict = mock_pv_data.model_dump()

    for key in unpacked_dict.keys():
        assert_equal_any(unpacked_dict.get(key), raw_dict.get(key))


@bindings_installed
@given(mock_pv_data())
def test_serialise_pv_data_from_python_object(fake_pv_data):
    from epac_flatbuffer_formats_rs import serialise_pv_data

    # main entry point so always test
    payload = serialise_pv_data(fake_pv_data)
    assert isinstance(payload, bytes)
    assert len(payload) > 0


@bindings_installed
@given(mock_pv_data())
def test_round_trip(mock_pv_data: PVData) -> None:
    try:
        _roundtrip(mock_pv_data, "rust")
    except Exception as rust_error:
        # try python roundtrip to see whether python also fails
        try:
            _roundtrip(mock_pv_data, "python")
        except Exception as py_error:
            # raise python failure
            raise Exception(
                f"\nPython serialisation also failed while rust serialisation failed:\n\n{py_error}"
            )

        # python passed, reraise the original rust error
        raise rust_error


# =======================================
# VERBOSE UNIT TESTS FOR FOUND EDGE CASES
# =======================================


@bindings_installed
def test_empty_array_roundtrip() -> None:
    empty_scalar = NTScalarAny(
        value=np.empty(
            [
                1,
            ]
        ),
        descriptor="",
        alarm=None,
        timeStamp=None,
        display=None,
        control=None,
    )
    empty_data = PVData(
        data=empty_scalar,
        sourceName="",
        pulseId=None,
    )
    _roundtrip(empty_data, "rust")


@bindings_installed
def test_array_with_256() -> None:
    val = NTScalarAny(
        value=np.array([256]),
        descriptor="",
        alarm=None,
        timeStamp=None,
        display=None,
        control=None,
    )
    data = PVData(
        data=val,
        sourceName="",
        pulseId=None,
    )
    _roundtrip(data, "rust")
