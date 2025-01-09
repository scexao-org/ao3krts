#!/usr/bin/env python
from __future__ import annotations

import numpy as np
from astropy.io import fits

import os

ROOTDIR_APD188 = os.environ['HOME'] + '/AOloop/apd188-rootdir'
#ROOTDIR_APD3K = os.environ['HOME'] + '/AOloop/apd3k-rootdir' # Unused here
ROOTDIR_PT = os.environ['HOME'] + '/AOloop/bimdm3kpt-rootdir'

# Prepare mask that cuts off BIM188 from DAC40 packets
# sizeof(DAC_buff_struct) == 420
dac_bim_mask = np.zeros(420 // 2, np.float32)  # 208 INT16 values
dac_bim_mask[8:8 + 188] = 1.0

# Load the control matrices

# --- curvature -> APD3k eigenmodes
APD3k_CMmodesWFS: np.ndarray = fits.getdata(ROOTDIR_PT +
                                            '/conf/CMmodesWFS_fromAPD3k.fits')
# --> n_modes x 1 x 188
n_modes = APD3k_CMmodesWFS.shape[0]
print(f'n_modes: {n_modes}')
if n_modes > 188:
    APD3k_CMmodesWFS = APD3k_CMmodesWFS[:188]

APD3k_CMmodesWFS_mat = APD3k_CMmodesWFS.view().squeeze()
# Renormalizer to operate within Olivier's conventions...
APD3k_CMmodesWFS_mat /= np.sum(APD3k_CMmodesWFS_mat**2, axis=1)[:, None]
# --> n_modes x 188

# --- APD3k eigenmodes -> DM3k maps
APD3k_CMmodesDM: np.ndarray = fits.getdata(ROOTDIR_PT +
                                           '/conf/CMmodesDM_fromAPD3k.fits')
if n_modes > 188:
    APD3k_CMmodesDM = APD3k_CMmodesDM[:188]
    n_modes = 188
# --> n_modes x 64 x 64
assert n_modes == APD3k_CMmodesDM.shape[0]  # Uh
APD3k_CMmodesDM_mat = APD3k_CMmodesDM.view().reshape(n_modes, 64 * 64)
# --> n_modes x 4096

# Modal gains
APD3k_modalGains: np.ndarray = fits.getdata(
        ROOTDIR_PT + '/conf/modalgains188.fits')[:n_modes]
# TODO OVERRIDE
#APD3k_modalGains = np.ones(n_modes)
# That curve was actually pretty agressive, so maybe a **p with p < 1 is indicated.
# n_modes

# CM_full = (APD3k_CMmodesDM.T @ APD3k_CMmodesWFS).T
# --- curvature -> DM3k maps
#CM_fromcurv = APD3k_CMmodesWFS_mat.T @ APD3k_CMmodesDM_mat
CM_fromcurv = APD3k_CMmodesWFS_mat.T @ (APD3k_CMmodesDM_mat *
                                        APD3k_modalGains[:, None]**1)
# --> 188 x 4096

# CM06
# --- curvature -> BIM commands
# As far a this transpose, no effing clue.s
CM06: np.ndarray = fits.getdata(ROOTDIR_APD188 + '/conf/ao188cmtx.fits')
# TODO OVERRIDE
CM06 = 2.22 * np.eye(188, dtype=np.float32)

# --> 188 x 188
CM06_expanded = np.zeros((210, 188), np.float32)
CM06_expanded[dac_bim_mask.astype(np.bool_)] = CM06
# --> 210 x 188

# RM06
# --- BIM commands -> curvature
RM06 = np.linalg.pinv(CM06, rcond=0.01)  # Should give all 187 modes
# --> 188 x 188
RM06_expanded = np.linalg.pinv(CM06_expanded, rcond=0.01)

# --> 210 x 188

# All together
# --- BIM commands -> ALPAO commands
CM_frombim = RM06_expanded.T @ CM_fromcurv
CM_frombim[8:8 + 18, :] *= 0.5
# --> 210 x 4096

SCALEDOWN_1 = 400 / 8192.  # scaledown from INT16 14bit to Volts
#SCALEDOWN_2 = 1e-5 # scaledown from volts to ouput units of the CM06 - should now be fixed

CM_frombim_reshapo_cubo = SCALEDOWN_1 * CM_frombim.copy().reshape(210, 64,
                                                                  64).copy()

# Write all to fits. Note per CACAO conventions, I'm adding a 1 dimension.
fits.writeto(ROOTDIR_PT + '/conf/DACBIMmask.fits',
             dac_bim_mask[None, :].astype(np.float32), overwrite=True)
fits.writeto(ROOTDIR_PT + '/conf/pt_matrix_bim2alpao.fits',
             CM_frombim_reshapo_cubo.astype(np.float32), overwrite=True)

# Write TT and focus vectors for RTS06.

# At this point, what's need is a FITS2shm and a R-cycle of mvalC2DM-9

print('Performing milk-FITS2shm....')

os.system(
        f'milk-FITS2shm {ROOTDIR_PT}/conf/pt_matrix_bim2alpao.fits aol9_CMmodesDM'
)
print('Now R-cycle the MVM process.....')

print('Writing oct files....')


def oct_read(path: str) -> np.ndarray:
    with open(path, 'r') as f:
        data = [[float(f) for f in line.strip().split()]
                for line in f.readlines() if not line.startswith('#')]

    return np.asarray(data).squeeze()


def oct_write(path: str, data: np.ndarray, name: str):
    if data.ndim == 1:
        data = data.view().reshape((1, len(data)))

    with open(path, 'w') as f:
        f.write('\n'.join([
                '# Created by refresh_matrices.py', f'# name: {name}',
                '# type: matrix', f'# rows: {data.shape[0]}',
                f'# columns: {data.shape[1]}'
        ]))
        f.write('\n')

        for ii in range(data.shape[0]):
            f.write(' '.join([str(fl) for fl in data[ii]]))
            if ii < data.shape[0] - 1:
                f.write('\n')


oct_read_tt = oct_read(ROOTDIR_PT + '/conf/ao188ttctrl_rts23_from.oct')  # 2x188
oct_read_fcs = oct_read(ROOTDIR_PT +
                        '/conf/ao188dfcsctrl_rts23_from.oct')  # 188

# Compute gross projections just to get the sign right

projected_mat = np.linalg.pinv(APD3k_CMmodesWFS_mat[:2]).T @ oct_read_tt.T
new_tt_vectors = projected_mat @ APD3k_CMmodesWFS_mat[:2]
#new_tt_vectors /= np.sum(new_tt_vectors**2, axis=1)[:,None]

projected_fcs = np.linalg.pinv(APD3k_CMmodesWFS_mat[2:3]).T @ oct_read_fcs
new_fcs_vector = projected_fcs * APD3k_CMmodesWFS_mat[2]
#new_fcs_vector /= np.sum(new_fcs_vector**2)

fits.writeto(ROOTDIR_PT + '/conf/ao188ttctrl_rts23.fits', new_tt_vectors,
             overwrite=True)
fits.writeto(ROOTDIR_PT + '/conf/ao188dfcsctrl_rts23.fits', new_fcs_vector,
             overwrite=True)

oct_write(ROOTDIR_PT + '/conf/ao188ttctrl_rts23.oct', new_tt_vectors, 'ttctrl')
oct_write(ROOTDIR_PT + '/conf/ao188dfcsctrl_rts23.oct', new_fcs_vector,
          'dmdfcs')
