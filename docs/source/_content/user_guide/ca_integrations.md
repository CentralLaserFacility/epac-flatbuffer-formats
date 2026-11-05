# Channel Access integrations

For Channel Access scalar values that should use `pva0`, `CaToNtConverter`
converts a `CAScalarAny` model or a matching dictionary into an `NTScalarAny`.
The converted value can then be placed in a `PVData` object and serialized as
usual:

```python
from epac.flatbuffers.ca_to_pva import CaToNtConverter
from epac.flatbuffers.data_types import PVData
from epac.flatbuffers.pva0_data import serialise_data

ca_value = {
    "value": 42.5,
    "pvname": "MY:PV:NAME",
    "status": 1,
    "precision": 2,
    "units": "V",
    "severity": 0,
    "timestamp": 1713201234.567,
    "upper_disp_limit": 100.0,
    "lower_disp_limit": 0.0,
    "upper_ctrl_limit": 95.0,
    "lower_ctrl_limit": 5.0,
}
nt_scalar = CaToNtConverter().convert_scalar(ca_value)
pv_data = PVData(sourceName=ca_value["pvname"], data=nt_scalar)
buffer = serialise_data(pv_data)
```

The converter currently handles scalars only; Channel Access waveform
conversion is not implemented.

````{note}
The dictionary format used by `CaToNtConverter` is the same as provided by `pyepics`.

Request control metadata as well to include fields such as units, precision, and limits.

For example, using `PV.get_with_metadata()`:

```python
from epics import PV
from epac.flatbuffers.ca_to_pva import CaToNtConverter

pv = PV("MY:PV:NAME", form="time")
ca_value = pv.get_with_metadata(with_ctrlvars=True)
if ca_value is None:
    raise RuntimeError(f"Could not read {pv.pvname}")

nt_scalar = CaToNtConverter().convert_scalar(ca_value)
```

````