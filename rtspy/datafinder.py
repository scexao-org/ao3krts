'''
    The (passive) state-machine class for the AO188 APD NGS/LGS modes.

    Multiple instance should be permitted

    Of course bindings are very custom to the exact setup of the AO188 RTS.
'''
from __future__ import annotations

# Typing
import typing as typ

# Stock external
import numpy as np

# Homemade external
from pyMilk.interfacing.shm import SHM

# Internal
from . import config
from .datafetch import fetcher




class RtmDataSupervisor:

    def __init__(self) -> None:
        '''
            Maybe try to write something a little more automatable...
            "Fetch by topic"
            Where topic / topic interfaces (SHM, FPS+param name) are readily identified.
        '''

        self.DATA_VAULT = {}

        # APD FETCHER IS SPECIAL, because its 2x216 and we should only have 1x216.
        # TODO: get the correct latest frame
        self.apd_fetcher = fetcher.APD2DFetcher(self, 'APD_DATA_ARR', config.SHMNAME_APD,
                                      shm_callables = {
                                            'FRAME_NUMBER': SHM.get_counter,
                                      },
                                      data_callables = {
                                            'APD_CELLDATAMIN': lambda x: np.min(x[:188]),
                                            'APD_CELLDATAMAX': lambda x: np.max(x[:188]),
                                            'APD_CELLDATAVAR': lambda x: np.var(x[:188]),
                                            'APD_CELLDATAAVG': lambda x: np.mean(x[:188]),
                                      })

        self.curvature_fetcher = fetcher.SHMFetcher(self, 'CURV_DATA_ARR', config.SHMNAME_CURV1K,
                                       data_callables = {
                                            'CURV_CELLDATAMIN': lambda x: np.min,
                                            'CURV_CELLDATAMAX': lambda x: np.max,
                                            'CURV_CELLDATAVAR': lambda x: np.var,
                                            'CURV_CELLDATAAVG': lambda x:np.mean,
                                      })

        self.bim188_fetcher = fetcher.SHMFetcher(self, 'BIM188_DATA_ARR', config.SHMNAME_APD,
                                         data_callables = {
                                             'DM_CELLDATAMIN': np.min,
                                             'DM_CELLDATAMAX': np.max,
                                             'DM_CELLDATAVAR': np.var,
                                             'DM_CELLDATAAVG': np.mean,
                                         })

        # TODO: have a pointer to the correct curvature.
        self.curv_shm = SHM(config.HOWFS_SHM)

        self.apd_shm = SHM(config.SHMNAME_APD)
        self.bim188_shm = SHM(config.SHMNAME_DM)

        self.tt_shm = SHM(config.SHMNAME_TT)
        self.wtt_shm = SHM(config.SHMNAME_WTT)
        self.ctt_shm = SHM(config.SHMNAME_CTT)


        '''
        General data (legacy order) subsection, for reference.
        '''
        FRAME_NUMBER = 0 ## OK
        DM_CELLDATAMIN = 23 ## OK
        DM_CELLDATAMAX = 24 ## OK
        DM_CELLDATAVAR = 25 ## OK
        DM_CELLDATAAVG = 26 ## OK
        CRV_CELLDATAMIN = 39 ## OK
        CRV_CELLDATAMAX = 40 ## OK
        CRV_CELLDATAVAR = 41 ## OK
        CRV_CELLDATAAVG = 42 ## OK
        APD_CELLDATAMIN = 51 ## OK
        APD_CELLDATAMAX = 52 ## OK
        APD_CELLDATAVAR = 53 ## OK
        APD_CELLDATAAVG = 54 ## OK # changed APD_CELLCOUNTAVG APD_CELLDATAAVG

        VMFREQ = 2 ## ??
        VMVOLT = 3 ## ??
        APD_RMAGAVG = 55 ## ??
        IRM2TTX = 77 # ??
        IRM2TTY = 78 # ??
        IRM2TTVAR = 79 # ??
        
        VMDRIVE = 1
        VMPHASE = 4
        LOOPSTATUS = 5
        DMGAIN = 6 # HOWFS loop gain?
        DMGAINHOLD = 7
        TTGAIN = 8
        TTGAINHOLD = 9
        PSUBGAIN = 10
        PSUBGAINHOLD = 11
        STTGAIN = 12
        STTGAINHOLD = 13
        HTTGAIN = 14
        HDFGAIN = 15
        LTTGAIN = 16
        LDFGAIN = 17
        WTTGAIN = 18
        ADFGAIN = 19
        CTRLMTRXSIDE = 20
        APDSAFETY = 21
        DMSAFETY = 22
        DM_TTMODEX = 27
        DM_TTMODEY = 28
        DM_TTMODEVAR = 29
        DM_DEFOCUS = 30  # dm defocus slider: -1 to 1
        DM_DEFOCUSVAR = 31  #
        DM_FLATVAR = 32
        DM_TIMEVAR = 33
        DM_TTMOUNTX = 34  # -9 to 9 top tiptilt mount plot
        DM_TTMOUNTY = 35  # -9 to 9 top tiptilt mount plot
        DM_TTMOUNTVAR = 36
        DM_TTMOUNTFLATVAR = 37
        DM_TTMOUNTTIMEVAR = 38
        CRV_TTMODEX = 43
        CRV_TTMODEY = 44
        CRV_TTMODEVAR = 45
        CRV_DEFOCUS = 46  # crv defocus slider -1 to 1 usually -0.1 to 0.1
        CRV_DEFOCUSVAR = 47
        CRV_FLATVAR = 48
        CRV_TIMEVAR = 49
        CRV_WAVEFRONTERROR = 50
        LWF_DATAMIN = 56
        LWF_DATAMAX = 57
        LWF_DATAVAR = 58
        LWF_COUNTAVG = 59
        LWF_RMAGAVG = 60  # sh label: rmag
        LWF_TTMODEX = 61  # sh dot plot -1 to 1
        LWF_TTMODEY = 62  # sh dot plot -1 to 1
        LWF_TTMODEVAR = 63
        LWF_DEFOCUS = 64  # sh defocus slider
        LWF_DEFOCUSVAR = 65
        SH_Q1TTMODEX = 66
        SH_Q1TTMODEY = 67
        SH_Q2TTMODEX = 68
        SH_Q2TTMODEY = 69
        SH_Q3TTMODEX = 70
        SH_Q3TTMODEY = 71
        SH_Q4TTMODEX = 72
        SH_Q4TTMODEY = 73
        WFS_TTCH1 = 74  # 0 to 10 both tiptilt mount plot X
        WFS_TTCH2 = 75  # 0 to 10 both tiptilt mount plot Y
        WFS_VAR = 76
        GENDATASZ = 80

    
    def __getitem__(self, key: typ.Any) -> typ.Any:
        return self.DATA_VAULT[key]

    def __setitem__(self, key: typ.Any, value: typ.Any) -> None:
        self.DATA_VAULT[key] = value
        
    def process_data(self) -> None:
        # Now all the custom bits.
        pass

    def send(self) -> None:
        pass
    