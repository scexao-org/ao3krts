from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

import numpy as np

from .dispatcher import ClickInvokableObjectForServer, locking_func_decorator

from pyMilk.interfacing.shm import SHM

from .. import config


class TestControl(ClickInvokableObjectForServer):
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

    @self.click_invokator.command('x')
    @locking_func_decorator
    def x_func(self) -> float:
        print('Calling x')
        return 1.0

    @self.click_invokator.command('x')
    @locking_func_decorator
    def y_func(self, **kwargs):
        print('Calling y')
        print(kwargs)
        return 3.1415
