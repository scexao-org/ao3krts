from __future__ import annotations
import typing as typ

import os

from enum import Enum, IntEnum

FILE_RTSMODE = '/tmp/RTS_CURRENTMODE.txt'


class MacroRetcode(IntEnum):
    OK = 0
    ERR = 1


if typ.TYPE_CHECKING:
    T_RetCodeMessage: typ.TypeAlias = tuple[MacroRetcode, str]
    T_MacroFunction: typ.TypeAlias = typ.Callable[[], T_RetCodeMessage]
    T_StartStopPair: typ.TypeAlias = tuple[T_MacroFunction, T_MacroFunction]


class RTS_MODULE_ENUM(str, Enum):
    # Note: for the click parser, left and right DO need to match
    # HW
    IIWI = 'IIWI'
    DAC40 = 'DAC40'
    APD = 'APD'
    PT_APD = 'PT_APD'
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


class RTS_MODULE(typ.Protocol):
    MODULE_NAMETAG: RTS_MODULE_ENUM
    '''
    MANDATORY BOILERPLATE FOR SUBCLASSES:

    Import and register in dict_module_modes.py
    '''
    '''
    def __init__(self) -> None:
        # This will actually never be called since this is a protocol,
        # not an abstract class
        raise TypeError('No can instantiate static namespace-like class.')
    '''

    @classmethod
    def start_function(cls, config_mode: str | None = None) -> T_RetCodeMessage:
        ...

    @classmethod
    def stop_function(cls) -> T_RetCodeMessage:
        ...


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
