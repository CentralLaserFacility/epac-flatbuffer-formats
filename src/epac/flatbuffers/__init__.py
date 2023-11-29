# Copied from https://github.com/ess-dmsc/python-streaming-data-types
# Upstream commit 3c2564cd6d

from .area_detector_ADAr import deserialise_ADAr, serialise_ADAr
from .logdata_f142 import deserialise_f142, serialise_f142
# from .arrays_wa00 import deserialise_wa00, serialise_wa00

SERIALISERS = {
    "f142": serialise_f142,
    "ADAr": serialise_ADAr,
    # "wa00": serialise_wa00,
}


DESERIALISERS = {
    "f142": deserialise_f142,
    "ADAr": deserialise_ADAr,
    # "wa00": deserialise_wa00,
}
