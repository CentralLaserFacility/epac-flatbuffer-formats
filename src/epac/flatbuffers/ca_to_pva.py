import epac.flatbuffers.data_types as dt


def cascalarall_to_ntscalarall(data: dt.CAScalarAll) -> dt.NTScalarAll:
    alarm = dt.AlarmT(severity=data.severity, status=data.status)

    timeStamp = dt.TimeT(
        secondsPastEpoch=int(data.timestamp),
        nanoseconds=int((data.timestamp - int(data.timestamp)) * 1e9),
    )

    display = dt.DisplayT(
        limitLow=data.lower_disp_limit,
        limitHigh=data.upper_disp_limit,
        units=data.units,
        precision=data.precision or dt.DisplayT().precision,
    )

    control = dt.ControlT(
        limitLow=data.lower_ctrl_limit,
        limitHigh=data.upper_ctrl_limit,
    )

    return dt.NTScalarAll(
        value=data.value,
        alarm=alarm,
        timeStamp=timeStamp,
        display=display,
        control=control,
    )
