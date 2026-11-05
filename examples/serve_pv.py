"""
Example script for serving a PV over PVAccess.
"""

from p4p.nt import NTScalar
from p4p.server import Server
from p4p.server.thread import SharedPV

pv = SharedPV(nt=NTScalar("d"), initial=42)

print("Serving PV 'EXAMPLE:PV' with value.")
Server.forever(providers=[{"EXAMPLE:PV": pv}])
