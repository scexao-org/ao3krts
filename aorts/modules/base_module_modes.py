from __future__ import annotations
import typing as typ

import os

from enum import Enum, IntEnum

FILE_RTSMODE = '/tmp/RTS_CURRENTMODE.txt'


class OkErrEnum(IntEnum):
    OK = 0
    ERR = 1


if typ.TYPE_CHECKING:
    T_Result: typ.TypeAlias = tuple[OkErrEnum, str]
    T_ResFunction: typ.TypeAlias = typ.Callable[[], T_Result]
    T_ResFunctionPair: typ.TypeAlias = tuple[T_ResFunction, T_ResFunction]


class RTS_MODULE_ENUM(str, Enum):
    '''
    Enumeration of the RTS modules keys throughout the codebase

    It is not indispensible, but is used by the parsers (CLI + remote server)
    to know if a mode is supposed to exist or not!
    '''
    # Note: for the click parser, left and right DO need to match
    # HW
    IIWI = 'IIWI'
    DAC40 = 'DAC40'
    APD = 'APD'
    # PT_APD = 'PT_APD' # DEPRECATED. APD just always passes-through.
    PT_DAC = 'PT_DAC'
    DM3K = 'DM3K'
    KWFS = 'KWFS'
    # LOOPS
    NIRLOOP = 'NIRLOOP'
    HOLOOP = 'HOLOOP'
    LOLOOP = 'LOLOOP'
    KWFSLOOP = 'KWFSLOOP'
    TTOFFL = 'TTOFFL'
    PTLOOP = 'PTLOOP'
    # MISC
    WTTOFF = 'WTTOFF'
    FOCOFF = 'FOCOFF'
    # TEST
    TEST = 'TEST'


class CONFIG_SUBMODES_ENUM(str, Enum):
    '''
    Enumeration of the RTS modules configurations for configurables
    Essentially this is just used as a safe-typing option

    It is not indispensible, but is used by the parsers (CLI + remote server)
    to know if a mode is supposed to exist or not!
    '''
    # Note: for the click parser, left and right DO need to match
    NGS = 'NGS'
    OLGS = 'OLGS'
    NLGS = 'NLGS'
    TT = 'TT'


class RTS_MODULE(typ.Protocol):
    MODULE_NAMETAG: RTS_MODULE_ENUM
    '''
    MANDATORY BOILERPLATE FOR SUBCLASSES:

    Import and register in dict_module_modes.py
    '''

    @classmethod
    def start_function(cls) -> T_Result:
        ...

    @classmethod
    def stop_function(cls) -> T_Result:
        ...


class RTS_MODULE_RECONFIGURABLE(RTS_MODULE, typ.Protocol):

    CFG_NAMES: list[CONFIG_SUBMODES_ENUM]

    @classmethod
    def reconfigure(cls, mode: CONFIG_SUBMODES_ENUM) -> T_Result:
        '''
        Hypothesis: reconfigure should NOT require the module to be started, even
        partially. Actually, it should require that the module is FULLY stopped.
        '''

        # assert mode in cls.CFG_NAMES <- should be there!

        ...

    @classmethod
    def configure_and_start(cls, mode: CONFIG_SUBMODES_ENUM | None = None
                            ) -> T_Result:
        ...


def proto_func_static_test_RTS_MODULE(mod: RTS_MODULE) -> None:
    pass


def proto_func_static_test_RTS_MODULE_RECONFIGURABLE(
        mod: RTS_MODULE_RECONFIGURABLE) -> None:
    pass


class ThisClass:
    MODULE_NAMETAG: RTS_MODULE_ENUM = RTS_MODULE_ENUM.TEST

    CFG_NAMES = []  # 0 is default!!

    @classmethod
    def start_function(cls) -> T_Result:
        return OkErrEnum.OK, ''

    @classmethod
    def stop_function(cls) -> T_Result:
        return OkErrEnum.OK, ''

    @classmethod
    def reconfigure(cls, mode: CONFIG_SUBMODES_ENUM) -> T_Result:
        assert mode in cls.CFG_NAMES
        return OkErrEnum.OK, ''

    @classmethod
    def configure_and_start(cls, mode: CONFIG_SUBMODES_ENUM | None = None
                            ) -> T_Result:
        if mode is None:
            mode = CONFIG_SUBMODES_ENUM(cls.CFG_NAMES[0])
        assert mode in cls.CFG_NAMES

        rc, msg = cls.reconfigure(mode)
        if rc == OkErrEnum.ERR:
            return rc, msg
        return cls.start_function()


proto_func_static_test_RTS_MODULE(ThisClass())
proto_func_static_test_RTS_MODULE_RECONFIGURABLE(ThisClass())


class RTS_MODE_ENUM(str, Enum):
    # Note: for the click parser, left and right DO need to match
    TEST = 'TEST'
    UNKNOWN = 'UNKNOWN'
    NONE = 'NONE'

    NIR188 = 'NIR188'
    NIR3K = 'NIR3K'
    CWFS_NGS188 = 'CWFS_NGS188'
    CWFS_NGS3K = 'CWFS_NGS3K'
    PT188 = 'PT188'
    PT3K = 'PT3K'

    @classmethod
    def _missing_(cls, value: str) -> RTS_MODE_ENUM:
        return cls.UNKNOWN

    @classmethod
    def write_rtsmode(cls, mode: RTS_MODE_ENUM):
        with open(FILE_RTSMODE, 'w') as f:
            f.write(mode.value + '\n')

    @classmethod
    def read_rtsmode(cls) -> RTS_MODE_ENUM:
        if not os.path.isfile(FILE_RTSMODE):
            return RTS_MODE_ENUM.NONE

        with open(FILE_RTSMODE, 'r') as f:
            return RTS_MODE_ENUM(f.readline().strip())
