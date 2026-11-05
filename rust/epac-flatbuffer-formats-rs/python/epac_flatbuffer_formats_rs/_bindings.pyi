from epac.flatbuffers.data_types import PVData

def serialise_pv_data(data: PVData) -> bytes:
    """Serialise a ``PVData`` object to bytes.

    Args:
        data (PVData): The ``PVData`` object to serialise.

    Returns:
        bytes: The serialised data.

    Example:

    .. code-block:: python

            from epac_flatbuffer_formats_rs import serialise_pv_data
            from epac.flatbuffers.data_types import PVData

            data = PVData(...)

            # serialise with rust
            payload = serialise_pv_data(data)

            assert len(payload)>0
            assert isinstance(payload, bytes)

    """
