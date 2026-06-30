from epac.flatbuffers import data_types as dt

from typing import Tuple


def float_to_time_components(timestamp: float) -> Tuple[int, int]:
    """Convert float seconds -> (seconds, nanoseconds)"""
    seconds = int(timestamp)
    nanoseconds = int((timestamp - seconds) * 1e9)
    return seconds, nanoseconds


def subtract_exposure_time(timestamp: dt.TimeT, exposure_time: float) -> dt.TimeT:
    """Subtract exposure_time (float seconds) from a TimeT object.

    Args:
    - ts: TimeT
    - exposure_time: float seconds

    Returns: TimeT object after subtraction
    """

    # Convert exposure time
    exposure_time_s, exposure_time_ns = float_to_time_components(exposure_time)

    data_timestamp_s = timestamp.secondsPastEpoch
    data_timestamp_ns = timestamp.nanoseconds

    # Borrow if needed for nanoseconds subtraction
    if data_timestamp_ns < exposure_time_ns:
        data_timestamp_ns += int(1e9)
        data_timestamp_s -= 1

    data_timestamp_ns -= exposure_time_ns
    data_timestamp_s -= exposure_time_s

    return dt.TimeT(secondsPastEpoch=data_timestamp_s, nanoseconds=data_timestamp_ns)
