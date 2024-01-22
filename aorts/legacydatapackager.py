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
if typ.TYPE_CHECKING:
    from .datafinder import RTMDataSupervisor

import numpy as np

RTM_PAYLOAD_SIZE = 660


class RTM_PAYLOAD:
    DM = np.s_[:188]
    CURV = np.s_[188:188 + 188]
    HOWFS_APD = np.s_[376:376 + 188]
    LOWFS_APD = np.s_[564:564 + 16]
    MISC = np.s_[580:]


class APD_PAYLOAD:
    HOWFS = np.s_[:188]
    LOWFS = np.s_[188:188 + 16]


class ZmqDataPackagerSender:
    '''
        Holds an instance of the RtmDataSupervisor

        Knows how to serialize frames

        Spins up a clocked thread

        Clocked thread feeds zmq socket
    '''

    def __init__(self, rtmDataSupervisor: RTMDataSupervisor) -> None:

        self.buffer = np.zeros(RTM_PAYLOAD_SIZE, '<f4')
        self.data_mgr = rtmDataSupervisor

    def bufferize_data(self) -> None:
        # DM telemetry
        self.buffer[RTM_PAYLOAD.DM] = self.data_mgr.get_array('BIM188_DATA_ARR')
        # Curvature data
        self.buffer[RTM_PAYLOAD.CURV] = self.data_mgr.get_array('CURV_DATA_ARR')
        # HOWFS APD readout
        self.buffer[RTM_PAYLOAD.HOWFS_APD] = self.data_mgr.get_array(
                'APD_DATA_ARR')[APD_PAYLOAD.HOWFS]
        # Shack APD readout
        self.buffer[RTM_PAYLOAD.LOWFS_APD] = self.data_mgr.get_array(
                'APD_DATA_ARR')[APD_PAYLOAD.LOWFS]
        # Misc data tail - assumes we've done _bufferize_aux_data
        self.buffer[RTM_PAYLOAD.MISC] = self.data_mgr.aux_arr

    def legacy_string_bufferize(self) -> None:
        pass
