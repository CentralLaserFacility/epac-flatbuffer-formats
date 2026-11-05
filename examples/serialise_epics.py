"""
Example script for serialising and deserialising a live EPICS PV to and from flatbuffer
bytes.
"""

from p4p.client.thread import Context

from epac.flatbuffers.data_types import NTScalarAny, PVData
from epac.flatbuffers.pva0_data import deserialise_data, serialise_data

pv_name = "EXAMPLE:PV"  # Replace with a PV available over PVAccess.
context = Context("pva", nt=False)
epics_value = context.get(pv_name)

pv_data = PVData(
    sourceName=pv_name,
    data=NTScalarAny(**epics_value.todict()),
)

buffer = serialise_data(pv_data)
restored = deserialise_data(buffer)

print(restored.sourceName)
print(restored.data.value)  # type: ignore[union-attr]
