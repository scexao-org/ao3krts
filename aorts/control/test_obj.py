from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

import numpy as np

from .dispatcher import DocoptDispatchingObject, locking_func_decorator

from pyMilk.interfacing.shm import SHM

from .. import config


class TestControl(DocoptDispatchingObject):
    NAME = 'TEST'

    DESCR = 'Simple debug object'

    DOCOPTSTR = '''
Usage:
    test x <val>
    test y [-a <a>] [-b <b>]

Options:
    -a=<a>  Some value for a [default: PROUT]
    -b=<b>  Some value for a [default: 3.1415]
'''

    DOCOPTCASTER = {'<val>': float, '-a': str, '-b': float}

    def __init__(self) -> None:
        self.TCP_CALLS = {
                'x': self.x_func,
                'y': self.y_func,
        }

    def function_dispatch(self, cmd: str) -> str:
        return str(super().function_dispatch(cmd))

    @locking_func_decorator
    def x_func(self, **kwargs):
        print('Calling x')
        print(kwargs)
        return 1.0

    @locking_func_decorator
    def y_func(self, **kwargs):
        print('Calling y')
        print(kwargs)
        return 3.1415
