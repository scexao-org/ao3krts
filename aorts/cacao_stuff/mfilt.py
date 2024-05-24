from __future__ import annotations

import typing as typ

from pyMilk.interfacing.fps import FPS


class MFilt(FPS):

    def __init__(self, name: str) -> None:
        super().__init__(name)

    @classmethod
    def cast_from_FPS(cls, fps: FPS) -> MFilt:
        fps.__class__ = MFilt  # yes, that's a cast ;)
        return fps  # type: ignore

    def loop_open(self) -> None:
        self.set_param('loopON', False)

    def loop_close(self) -> None:
        self.set_param('loopON', True)

    def get_loop_status(self) -> bool:
        return self.get_param('loopON')

    def get_gain(self) -> float:
        return self.get_param('loopgain')  # type: ignore

    def set_gain(self, gain: float) -> None:
        self.set_param('loopgain', gain)

    def set_mult(self, mult: float) -> None:
        self.set_param('loopmult', mult)

    def get_mult(self) -> float:
        return self.get_param('loopmult')  # type: ignore

    def set_modlimit(self, limit: float) -> None:
        self.set_param('looplimit', limit)
