#!/usr/bin/env python
'''
Reset DAC40 TT mount to 0V (midrange)

Usage:
    tt_zero.py [all]
'''


from docopt import docopt

from pyMilk.interfacing.shm import SHM

import logging
from swmain.infra.logger import init_logger_autoname


if __name__ == "__main__":
    args = docopt(__doc__) # no args - but will crash if there are args that should be there.
    init_logger_autoname()
    logg = logging.getLogger()
    
    if args['all']:
        logg.info('TT mount: zeroing all dm01dispXX channels.')
        for ch in range(12):
            dmch = SHM(f'dm01disp{ch:02d}')
            dmch.set_data(0.0 * dmch.get_data())
    
    tt_float = SHM('tt_value_float')
    
    tt_float.set_data(0.0 * tt_float.get_data())
    
    logg.info('TT mount zeroed through tt_value_float')