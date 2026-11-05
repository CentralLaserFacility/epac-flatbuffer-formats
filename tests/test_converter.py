import pytest

import epac.flatbuffers.data_types as dt
from epac.flatbuffers.ca_to_pva import CaToNtConverter


@pytest.fixture
def converter():
    return CaToNtConverter()


@pytest.mark.parametrize(
    "severity, ca_status, expected_status, expected_message",
    [
        (0, 0, dt.AlarmStatus.NONE, "NO_ALARM"),
        (1, 3, dt.AlarmStatus.DEVICE, "HIHI"),
        (2, 9, dt.AlarmStatus.DRIVER, "COMM"),
        (3, 15, dt.AlarmStatus.RECORD, "SOFT"),
        (0, 20, dt.AlarmStatus.DB, "READ_ACCESS"),
        (1, 999, dt.AlarmStatus.UNDEFINED, "undefined alarm status"),  # Invalid status
    ],
)
def test_create_alarm(
    converter, severity, ca_status, expected_status, expected_message
):
    result = converter.create_alarm(severity, ca_status)

    assert isinstance(result, dt.AlarmT)
    assert result.severity == severity
    assert result.status == expected_status
    assert result.message == expected_message


@pytest.mark.parametrize(
    "timestamp, expected_seconds, expected_nanoseconds",
    [
        (1741081171.628057718, 1741081171, 628057718),
        (0.0, 0, 0),  # Unix epoch start
    ],
)
def test_create_timestamp(converter, timestamp, expected_seconds, expected_nanoseconds):
    result = converter.create_timestamp(timestamp)

    assert isinstance(result, dt.TimeT)
    assert result.secondsPastEpoch == expected_seconds
    assert result.nanoseconds == expected_nanoseconds


def test_create_display(converter):
    result = converter.create_display(1.5, 10.5, "m", 2)

    assert isinstance(result, dt.DisplayT)
    assert result.limitLow == 1.5
    assert result.limitHigh == 10.5
    assert result.units == "m"
    assert result.precision == 2


def test_create_control(converter):
    result = converter.create_control(-5.0, 5.0)

    assert isinstance(result, dt.ControlT)
    assert result.limitLow == -5.0
    assert result.limitHigh == 5.0


def test_convert_scalar(converter):
    test_data_dict = {
        "value": [47, 104, 111, 109],
        "severity": 2,  # MAJOR
        "status": 3,  # HIHI
        "timestamp": 1741081171.628057718,
        "lower_disp_limit": 5.0,
        "upper_disp_limit": 1.0,
        "units": "u",
        "precision": 2,
        "lower_ctrl_limit": 5.0,
        "upper_ctrl_limit": 1.0,
    }

    result = converter.convert_scalar(test_data_dict)

    # check correct data types are created with correct values
    assert isinstance(result, dt.NTScalarAny)
    assert result.value == [47, 104, 111, 109]

    assert isinstance(result.alarm, dt.AlarmT)
    assert result.alarm.status == dt.AlarmStatus.DEVICE
    assert result.alarm.severity == dt.AlarmSeverity.MAJOR
    assert result.alarm.message == CaToNtConverter.CaAlarmStatus.HIHI.name

    assert isinstance(result.timeStamp, dt.TimeT)
    assert result.timeStamp.secondsPastEpoch == int(test_data_dict["timestamp"])
    assert result.timeStamp.nanoseconds == int(
        (test_data_dict["timestamp"] - int(test_data_dict["timestamp"])) * 1e9
    )
    assert isinstance(result.display, dt.DisplayT)
    assert result.display.limitLow == test_data_dict["lower_disp_limit"]
    assert result.display.limitHigh == test_data_dict["upper_disp_limit"]
    assert result.display.units == test_data_dict["units"]
    assert result.display.precision == test_data_dict["precision"]
    assert isinstance(result.control, dt.ControlT)

    assert result.control.limitLow == test_data_dict["lower_ctrl_limit"]
    assert result.control.limitHigh == test_data_dict["upper_ctrl_limit"]

    # check result is the same if directly passed a ca scalar data type instead of a dictionary
    test_data_ca_scalar = dt.CAScalarAny(**test_data_dict)
    result_ca_scalar = converter.convert_scalar(test_data_ca_scalar)
    assert result == result_ca_scalar


def test_convert_scalar_missing_fields(converter):
    test_data_dict = {
        "value": [100],
        "timestamp": 1000.5,
    }

    result = converter.convert_scalar(test_data_dict)

    assert isinstance(result.alarm, dt.AlarmT)
    assert result.alarm.status == dt.AlarmStatus.NONE
    assert result.alarm.severity == 0
    assert result.alarm.message == "NO_ALARM"

    assert isinstance(result.display, dt.DisplayT)
    assert result.display.limitLow == 0.0
    assert result.display.limitHigh == 0.0
    assert result.display.units == ""
    assert result.display.precision == 0

    assert isinstance(result.control, dt.ControlT)
    assert result.control.limitLow == 0.0
    assert result.control.limitHigh == 0.0
