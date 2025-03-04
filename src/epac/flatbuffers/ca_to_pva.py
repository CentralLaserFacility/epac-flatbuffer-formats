from enum import IntEnum

import epac.flatbuffers.data_types as dt


class CaToNtConverter:
    class CaAlarmStatus(IntEnum):
        NO_ALARM = 0
        READ = 1
        WRITE = 2
        HIHI = 3
        HIGH = 4
        LOLO = 5
        LOW = 6
        STATE = 7
        COS = 8
        COMM = 9
        TIMEOUT = 10
        HW_LIMIT = 11
        CALC = 12
        SCAN = 13
        LINK = 14
        SOFT = 15
        BAD_SUB = 16
        UDF = 17
        DISABLE = 18
        SIMM = 19
        READ_ACCESS = 20
        WRITE_ACCESS = 21

    ALARM_TYPE = {
        CaAlarmStatus.NO_ALARM: dt.AlarmStatus.NONE,
        **{
            key: dt.AlarmStatus.DEVICE
            for key in [
                CaAlarmStatus.READ,
                CaAlarmStatus.WRITE,
                CaAlarmStatus.HIHI,
                CaAlarmStatus.HIGH,
                CaAlarmStatus.LOLO,
                CaAlarmStatus.LOW,
                CaAlarmStatus.STATE,
                CaAlarmStatus.COS,
                CaAlarmStatus.HW_LIMIT,
            ]
        },
        **{
            key: dt.AlarmStatus.DRIVER
            for key in [
                CaAlarmStatus.COMM,
                CaAlarmStatus.TIMEOUT,
                CaAlarmStatus.UDF,
            ]
        },
        **{
            key: dt.AlarmStatus.RECORD
            for key in [
                CaAlarmStatus.CALC,
                CaAlarmStatus.SCAN,
                CaAlarmStatus.LINK,
                CaAlarmStatus.SOFT,
                CaAlarmStatus.BAD_SUB,
            ]
        },
        **{
            key: dt.AlarmStatus.DB
            for key in [
                CaAlarmStatus.DISABLE,
                CaAlarmStatus.SIMM,
                CaAlarmStatus.READ_ACCESS,
                CaAlarmStatus.WRITE_ACCESS,
            ]
        },
    }

    UNDEFINED_ALARM = dt.AlarmStatus.UNDEFINED  # UNDEFINED

    @classmethod
    def create_alarm(cls, severity: int, ca_status: int) -> dt.AlarmT:
        """Creates and returns an AlarmT object."""
        try:
            alarm_status = cls.ALARM_TYPE[cls.CaAlarmStatus(ca_status)]
            alarm_msg = cls.CaAlarmStatus(ca_status).name
        except ValueError:
            alarm_status = cls.UNDEFINED_ALARM
            alarm_msg = "undefined alarm status"
        return dt.AlarmT(severity=severity, status=alarm_status, message=alarm_msg)

    @staticmethod
    def create_timestamp(timestamp: float) -> dt.TimeT:
        """Creates and returns a TimeT object."""
        return dt.TimeT(
            secondsPastEpoch=int(timestamp),
            nanoseconds=int((timestamp - int(timestamp)) * 1e9),
        )

    @staticmethod
    def create_display(
        limit_low: float, limit_high: float, units: str, precision: int
    ) -> dt.DisplayT:
        """Creates and returns a DisplayT object."""
        return dt.DisplayT(
            limitLow=limit_low,
            limitHigh=limit_high,
            units=units,
            precision=precision,
        )

    @staticmethod
    def create_control(limit_low: float, limit_high: float) -> dt.ControlT:
        """Creates and returns a ControlT object."""
        return dt.ControlT(
            limitLow=limit_low,
            limitHigh=limit_high,
        )

    @classmethod
    def convert_scalar(cls, data: dt.CAScalarAny | dict) -> dt.NTScalarAny:
        """Converts CAScalarAny or scalar ca dictionary to NTScalarAny."""
        if isinstance(data, dict):
            data = dt.CAScalarAny(**data)
        return dt.NTScalarAny(
            value=data.value,
            alarm=cls.create_alarm(severity=data.severity, ca_status=data.status),
            timeStamp=cls.create_timestamp(timestamp=data.timestamp),
            display=cls.create_display(
                limit_low=data.lower_disp_limit,
                limit_high=data.upper_disp_limit,
                units=data.units,
                precision=data.precision,
            ),
            control=cls.create_control(
                limit_low=data.lower_ctrl_limit, limit_high=data.upper_ctrl_limit
            ),
        )
