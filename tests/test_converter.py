import epac.flatbuffers.data_types as dt
from epac.flatbuffers.ca_to_pva import CaToNtConverter


class TestCaToNtConverter:
    def test_convert_scalar(self):
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

        converter = CaToNtConverter()
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

    def test_missing_data_defaults(self):
        test_data_dict = {
            "value": [47, 104, 111, 109],
            "timestamp": 1741081171.628057718,
        }

        test_data = dt.CAScalarAny(**test_data_dict)
        assert test_data.pvname == ""
        assert test_data.status == 0
        assert test_data.precision == 0
        assert test_data.units == ""
        assert test_data.severity == 0
        assert test_data.upper_disp_limit == 0.0
        assert test_data.lower_disp_limit == 0.0
        assert test_data.upper_ctrl_limit == 0.0
        assert test_data.lower_ctrl_limit == 0.0
