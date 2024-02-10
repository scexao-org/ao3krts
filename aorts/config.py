from __future__ import annotations

import os

from dataclasses import dataclass, fields

#######################
# LOOP AND DM NUMBERS #
#######################



@dataclass(frozen=True)
class LOOP_INFO:
    full_name: str
    n: int

    # Defining __iter__ to allow unpacking a LOOP_INFO object as if a tuple
    def __iter__(self):
        return (getattr(self, field.name) for field in fields(self))


LINFO_HOAPD_BIM188 = LOOP_INFO('ao3k-apd188', 1)
LINFO_LOAPD_BIM188 = LOOP_INFO('ao3k-lowfs188', 2)
LINFO_IRPYR_BIM188 = LOOP_INFO('ao3k-nirpyr188', 3)
LINFO_BIM2TTOFFLOAD = LOOP_INFO('ao3k-ttoff188', 4)

# Loops to BIM188
LOOPNUM_HOAPD_BIM188 = 1
LOOPNUM_LOAPD_BIM188 = 2
LOOPNUM_IRPYR_BIM188 = 3

# Loops to ALPAO
LOOPNUM_HOAPD_ALPAO = 6
LOOPNUM_LOAPD_ALPAO = 7
LOOPNUM_IRPYR_ALPAO = 8

# Offload to TT
LOOPNUM_BIM2TTOFFLOAD = 4
LOOPNUM_ALPAO2TT_OFFLOAD = 9

DMNUM_BIM188 = '00'
DMNUM_BIM188SIM = '10'
DMNUM_TT = '01'
DMNUM_TTSIM = '11'
DMNUM_ALPAO = '64'
DMNUM_ALPAOSIM = '65'

########################################
# SYSTEM (NON-CACAO-MANAGED) SHM NAMES #
########################################

SHMNAME_APD = 'apd'
SHMNAME_LOWFS = 'lowfs_data'

SHMNAME_CURV1K = 'curv_1kdouble'
SHMNAME_CURV2KS = 'curv_2kdouble'
SHMNAME_CURV2KD = 'curv_2ksingle'

SHMNAME_BIM188 = 'bim188_tele'
SHMNAME_TT = 'tt_telemetry'
SHMNAME_CTT = 'wtt_telemetry'
SHMNAME_WTT = 'ctt_telemetry'

HOWFS_SHM = f'aol{LOOPNUM_HOAPD_BIM188}_wfsim'

###################
# DATAVAULT STUFF #
###################


DATASTORE_PATH = os.environ.get('DATASTORE_PATH', os.environ['HOME'] + '/datastore')
