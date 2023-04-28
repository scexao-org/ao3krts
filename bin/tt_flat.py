#!/usr/bin/env python
'''
Loads the most recent (in alphabetical order...) flat file onto dm01disp00 (tt flat)

Usage:
    tt_flat.py
'''

import os
import glob

from docopt import docopt

from pyMilk.interfacing.shm import SHM

import logging
from swmain.infra.logger import init_logger_autoname

from astropy.io import fits
import numpy as np

HOME = os.environ['HOME']
CONF = HOME + '/conf/tt_flats'
TT_DM = '01'

if __name__ == "__main__":
    args = docopt(
        __doc__
    )  # no args - but will crash if there are args that should be there.
    init_logger_autoname()
    logg = logging.getLogger()

    most_alphabetical_flat = max(glob.glob(CONF + '/*.fits'))
    flat = fits.get_data(most_alphabetical_flat).astype(np.float32).squeeze() # astropy messing with endianess...

    tt_chan_0 = SHM(f'dm{TT_DM}disp00')

    tt_chan_0.set_data(flat)

    logg.info(
        f'TT mount flattened using {most_alphabetical_flat.split("/")[-1]} on dm{TT_DM}disp00.'
    )
