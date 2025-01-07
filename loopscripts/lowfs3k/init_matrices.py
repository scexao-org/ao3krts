#!/bin/env python

import os
import numpy as np, numpy.typing as npt
from astropy.io import fits

from aorts.cacao_stuff.loop_manager import CacaoConfigReader

# This is small, we apply the permutation the linear algebra way and that's that.
apd_loop_cfg = CacaoConfigReader('ao3k-apd3k', None)
loop_cfg = CacaoConfigReader('ao3k-lowfs3k', None)

FULLPATH = loop_cfg.rootdir / 'scripts'  # IF DONE RIGHT THIS SHOULD BE A SYMLINK TO REPO


def create_ttf_extraction_matrix() -> npt.NDArray[np.float32]:
    mat = np.zeros((3, 1, 11), np.float32)

    mat[0, 0, 8] = 1.0
    mat[1, 0, 9] = 1.0
    mat[2, 0,
        10] = 0.1  # Smaller because reasons (the way lowfs data is computed)? Note this only works asusming modenorm is disabled to wfs2cmodeval

    return mat


def create_ttf_to_dm_from_howfs(howfs_CMmodesDM: npt.NDArray[np.float32]
                                ) -> npt.NDArray[np.float32]:
    # A 90 deg rotation seems to do it right.
    submatrix = np.stack([
            -howfs_CMmodesDM[1, :, :],
            +howfs_CMmodesDM[0, :, :],
            +howfs_CMmodesDM[2, :, :],
    ], axis=0).astype(np.float32)

    # Change focus sign? Rotate tip-tilt?

    return submatrix


HOWFS_CMmodesDM_file = apd_loop_cfg.rootdir / 'conf' / 'CMmodesDM' / 'CMmodesDM.fits'
HOWFS_CMmodesDM: np.ndarray = fits.getdata(HOWFS_CMmodesDM_file)  # type: ignore

assert HOWFS_CMmodesDM.ndim == 3 and HOWFS_CMmodesDM.shape[1:] == (64, 64)

LOWFS_CMmodesWFS = create_ttf_extraction_matrix()
LOWFS_CMmodesDM = create_ttf_to_dm_from_howfs(HOWFS_CMmodesDM)

LOWFS_CMmodesWFS_file = loop_cfg.rootdir / 'conf' / 'CMmodesWFS' / 'CMmodesWFS.fits'
LOWFS_CMmodesDM_file = loop_cfg.rootdir / 'conf' / 'CMmodesDM' / 'CMmodesDM.fits'

# And now the million dollar question, what is the permutation convention and is a transpose needed here.
fits.writeto(LOWFS_CMmodesWFS_file, LOWFS_CMmodesWFS, overwrite=True)
fits.writeto(LOWFS_CMmodesDM_file, LOWFS_CMmodesDM, overwrite=True)

print('Done recomputing/saving LGS swap matrix.')
print(LOWFS_CMmodesWFS_file)
print(LOWFS_CMmodesDM_file)
