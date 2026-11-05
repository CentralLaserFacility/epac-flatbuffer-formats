"""
Example script for serialising and deserialising a PVData object to and from flatbuffer
bytes.
"""

from epac.flatbuffers.data_types import NTScalarAny, PVData
from epac.flatbuffers.pva0_data import deserialise_data, serialise_data

pv_data = PVData(
    sourceName="MY:PV:NAME",
    data=NTScalarAny(value=42),
)

buffer = serialise_data(pv_data)
with open("buffer.bin", "wb") as file:
    file.write(buffer)

with open("buffer.bin", "rb") as file:
    buffer = file.read()

restored = deserialise_data(buffer)

print(restored.sourceName)
print(restored.data.value)  # type: ignore[union-attr]
