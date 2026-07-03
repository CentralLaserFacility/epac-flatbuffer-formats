import pytest
import numpy as np

from epac.flatbuffers import data_types as dt


class TestExposure:
    source_name = "test-pv"
    pulseid = {"value": 1739946490, "timestamp": 1739946490.410324754}

    @pytest.mark.parametrize(
        "exposure_time_val",
        np.random.uniform(0.001, 1.0, size=10),
    )
    def test_exposure_time_calculation(self, exposure_time_val):

        nt_ndarray_dict = {
            "value": np.array([91, 92, 93, 102, 103, 104], dtype=np.uint8),
            "timeStamp": {
                "secondsPastEpoch": 1740045680,
                "nanoseconds": 233594955,
                "userTag": 0,
            },
            "attribute": [
                {
                    "name": "AcquireTime",
                    "value": exposure_time_val,
                    "descriptor": "",
                    "sourceType": 0,
                    "source": "",
                    "alarm": None,
                    "time": None,
                    "tags": [],
                },
            ],
        }

        nt_ndarray_obj = dt.NTNDArray(**nt_ndarray_dict)

        # extract data timestamp
        data_ts: dt.TimeT | None = nt_ndarray_obj.timeStamp
        assert data_ts is not None

        # extract exposure time
        exposure_time = None
        for attr in nt_ndarray_obj.attribute:
            if attr.name == "AcquireTime":
                exposure_time = attr.value
                break
        assert exposure_time is not None

        # compute modified timestamp
        modified_ts = data_ts - exposure_time

        data_ns_total = data_ts.secondsPastEpoch * 1e9 + data_ts.nanoseconds
        mod_ns_total = modified_ts.secondsPastEpoch * 1e9 + modified_ts.nanoseconds

        computed_exp_time = (data_ns_total - mod_ns_total) / 1e9
        assert computed_exp_time == pytest.approx(exposure_time_val, abs=1e-6)
