#!/usr/bin/env python
from __future__ import annotations

import os
import shutil

ROOTDIR_APD188 = os.environ['HOME'] + '/AOloop/apd188-rootdir'
ROOTDIR_APD3K = os.environ['HOME'] + '/AOloop/apd3k-rootdir'
ROOTDIR_PT = os.environ['HOME'] + '/AOloop/bimdm3kpt-rootdir'

shutil.copy(ROOTDIR_APD3K + '/conf/CMmodesWFS.fits',
            ROOTDIR_PT + '/conf/CMmodesWFS_fromAPD3k.fits')
shutil.copy(ROOTDIR_APD3K + '/conf/CMmodesDM.fits',
            ROOTDIR_PT + '/conf/CMmodesDM_fromAPD3k.fits')
