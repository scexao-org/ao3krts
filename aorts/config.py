#######################
# LOOP AND DM NUMBERS #
#######################

from dataclasses import dataclass, fields


@dataclass(frozen=True)
class LOOP_INFO:
    full_name: str
    n: int

    # Defining __iter__ to allow unpacking a LOOP_INFO object as if a tuple
    def __iter__(self):
        return (getattr(self, field.name) for field in fields(self))


LINFO_HOAPD_BIM188 = LOOP_INFO('ao3k-apd188', 1)
LINFO_LOAPD_BIM188 = LOOP_INFO('ao3k-lowfs188', 2)
LINFO_IRPYR_BIM188 = LOOP_INFO('ao3k-nirpyr188', 4)
LINFO_BIM2TTOFFLOAD = LOOP_INFO('ao3k-ttoff188', 5)

LOOPNUM_HOAPD_BIM188 = 1
LOOPNUM_LOAPD_BIM188 = 2
LOOPNUM_IRPYR_BIM188 = 4  # Why not 3? No can remember.
LOOPNUM_HOAPD_ALPAO = 6
LOOPNUM_LOAPD_ALPAO = 7
LOOPNUM_IRPYR_ALPAO = 8

LOOPNUM_BIM2TTOFFLOAD = 5
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

SHMNAME_BIM188 = 'bim188_tele'
SHMNAME_TT = 'tt_telemetry'
SHMNAME_CTT = 'wtt_telemetry'
SHMNAME_WTT = 'ctt_telemetry'

HOWFS_SHM = 'aol3_wfsim'
