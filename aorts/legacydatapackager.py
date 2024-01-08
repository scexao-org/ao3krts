'''
    What's the legacy packet like?

    Total should be 5000 bytes

    32 byte header. Leaves 4968 chars.

    Followed by parsable space-separated ascii float array.
        Total : 660 floats. 4968 / 660 = 7.5. So 7, minus space = 6, minus sign and dec point = 4.
        So, 5 digits + sign + space and pad to 5000 chars.

        0  -188: DM data            (188)
        188-376: Curvature data     (188)
        376-564: APD data           (188)
        564-580: SH data            (16)
        580-660: GenData?           (80)
                Gendata (means general data!)
                    frameN at pos 0.
                    all defined in cst!
                    something something LGS / NGS at pos 20. CTRLMTRXSIDE?



    CHANGED: we ditched the ascii float array idea.

    Now it's 660 4-byte <f4 floats.
    That always takes 660 * 4 = 2640 bytes, we maintain full precision, and that's that.
'''
from __future__ import annotations

import typing as typ

import numpy as np

RTM_PAYLOAD_SIZE = 660


class LegacyDataPackager:
    '''
        Holds an instance of the RtmDataSupervisor

        Knows how to serialize frames

        Spins up a clocked thread

        Clocked thread feeds zmq socket
    '''

    def __init__(self) -> None:
        self.numpy_buffer = np.zeros(RTM_PAYLOAD_SIZE, '<f4')

    def bufferize_data(self) -> None:
        # DM telemetry
        self.numpy_buffer[0:188] = self.dm_data
        # Curvature data
        self.numpy_buffer[188:376] = self.curvature_data
        # HOWFS APD readout
        self.numpy_buffer[376:564] = self.apd_data[curv, :188]
        # Shack APD readout
        self.numpy_buffer[564:580] = self.apd_data[curv, 188:204]
