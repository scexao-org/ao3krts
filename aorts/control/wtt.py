from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

import numpy as np

from pyMilk.interfacing.shm import SHM

from .. import config


class GenericTTControl:
    NAME: str

    def __init__(self):
        self.shm = SHM(self.NAME)

    def zero(self, zero_all: bool = False) -> None:
        self.set(5, 5)

    def x(self) -> float:
        return self.shm.get_data()[0]

    def y(self) -> float:
        return self.shm.get_data()[1]

    def xset(self, val_x: float) -> None:
        self.set(val_x, None)

    def yset(self, val_y: float) -> None:
        self.set(None, val_y)

    def set(self, val_x: float | None, val_y: float | None) -> None:
        buff = self.shm.get_data(copy=True)
        if val_x is not None:
            buff[0] = val_x
        if val_y is not None:
            buff[1] = val_y
        self.shm.set_data(buff)


class WTTControl(GenericTTControl):
    SHM_NAME = 'wtt_value_float'


class CTTControl(GenericTTControl):
    SHM_NAME = 'ctt_value_float'
