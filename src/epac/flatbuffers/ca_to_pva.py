from enum import Enum

import epac.flatbuffers.data_types as dt
from epac.flatbuffers.fbschemas.pva0.AlarmStatus import AlarmStatus


class PyEpicsConverter:
    class CAAlarmStatus(Enum):
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
        CAAlarmStatus.NO_ALARM.value: AlarmStatus.NONE,
        **{
            key: AlarmStatus.DEVICE
            for key in [
                CAAlarmStatus.READ.value,
                CAAlarmStatus.WRITE.value,
                CAAlarmStatus.HIHI.value,
                CAAlarmStatus.HIGH.value,
                CAAlarmStatus.LOLO.value,
                CAAlarmStatus.LOW.value,
                CAAlarmStatus.STATE.value,
                CAAlarmStatus.COS.value,
                CAAlarmStatus.HW_LIMIT.value,
            ]
        },
        **{
            key: AlarmStatus.DRIVER
            for key in [
                CAAlarmStatus.COMM.value,
                CAAlarmStatus.TIMEOUT.value,
                CAAlarmStatus.UDF.value,
            ]
        },
        **{
            key: AlarmStatus.RECORD
            for key in [
                CAAlarmStatus.CALC.value,
                CAAlarmStatus.SCAN.value,
                CAAlarmStatus.LINK.value,
                CAAlarmStatus.SOFT.value,
                CAAlarmStatus.BAD_SUB.value,
            ]
        },
        **{
            key: AlarmStatus.DB
            for key in [
                CAAlarmStatus.DISABLE.value,
                CAAlarmStatus.SIMM.value,
                CAAlarmStatus.READ_ACCESS.value,
                CAAlarmStatus.WRITE_ACCESS.value,
            ]
        },
    }

    UNDEFINED_ALARM = AlarmStatus.UNDEFINED  # UNDEFINED

    @classmethod
    def create_alarm(cls, severity: int, status: int) -> dt.AlarmT:
        """Creates and returns an AlarmT object."""
        alarm_status = cls.ALARM_TYPE.get(status, cls.UNDEFINED_ALARM)
        try:
            alarm_msg = cls.CAAlarmStatus(status).name
        except ValueError:
            alarm_msg = ""
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
    def cascalarany_to_ntscalarany(cls, data: dt.CAScalarAny) -> dt.NTScalarAny:
        """Converts CAScalarAny to NTScalarAny."""
        return dt.NTScalarAny(
            value=data.value,
            alarm=cls.create_alarm(severity=data.severity, status=data.status),
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
