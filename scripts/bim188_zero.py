#!/usr/bin/env python
'''
Reset DAC40 BIM188 to 0V (midrange)

Usage:
    bim188_zero.py [all]
'''

from docopt import docopt

from pyMilk.interfacing.shm import SHM

import logging
from swmain.infra.logger import init_logger_autoname

if __name__ == "__main__":
    args = docopt(
            __doc__
    )  # no args - but will crash if there are args that should be there.
    init_logger_autoname()
    logg = logging.getLogger()

    if args['all']:
        logg.info('BIM188: zeroing all dm00dispXX channels.')
        for ch in range(12):
            dmch = SHM(f'dm00disp{ch:02d}')
            dmch.set_data(0.0 * dmch.get_data())

    tt_float = SHM('bim188_float')  # Remember: this is a simlink to dm00disp

    tt_float.set_data(0.0 * tt_float.get_data())

    logg.info('BIM188: zeroed through bim188_float.')
