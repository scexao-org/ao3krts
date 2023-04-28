#!/usr/bin/env python
'''
Reset DAC40 WTT mount to 0V (for poweroff) or 5V (midrange)

Usage:
    wtt_zero.py (0|5)
'''

from docopt import docopt

from pyMilk.interfacing.shm import SHM

import logging
from swmain.infra.logger import init_logger_autoname

if __name__ == "__main__":
    args = docopt(__doc__) # no args - but will crash if there are args that should be there.
    init_logger_autoname()
    logg = logging.getLogger()
    
    if args['0']:
        value = 0.0
    else:
        value = 5.0
        
    logg.info(f'WTT mount: resetting to {value:.1f} volts.')
    
    wtt_float = SHM('wtt_value_float')
    
    wtt_float.set_data(0.0 * wtt_float.get_data() + value)
    
    logg.info('WTT mount zeroed through wtt_value_float')
