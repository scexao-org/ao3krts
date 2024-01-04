#!/usr/bin/env python
'''
Loads the most recent (in alphabetical order...) flat file onto dm01disp00 (tt flat)

Usage:
    bim188_flat.py [sim]
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
CONF = HOME + '/conf/bim_flats'
BIM_DM = '00'
BIM_DMSIM = '10'

if __name__ == "__main__":
    args = docopt(
            __doc__
    )  # no args - but will crash if there are args that should be there.
    init_logger_autoname()
    logg = logging.getLogger()

    DM = (BIM_DM, BIM_DMSIM)[args['sim']]

    most_alphabetical_flat = max(glob.glob(CONF + '/*.fits'))
    flat = fits.getdata(most_alphabetical_flat).astype(np.float32).squeeze()

    bim_chan_0 = SHM(f'dm{DM}disp00')

    bim_chan_0.set_data(flat)

    logg.info(
            f'TT mount flattened using {most_alphabetical_flat.split("/")[-1]} on dm{DM}disp00.'
    )
