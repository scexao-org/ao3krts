from __future__ import annotations

import typing as typ

import os, glob
import re
import pathlib
from datetime import datetime
import numpy as np
from astropy.io import fits

import logging

logg = logging.getLogger()

from pyMilk.interfacing.shm import SHM


def save_by_folderpath(folder_fullpath: pathlib.Path, data: np.ndarray,
                       file_head_name: str | None = None,
                       time_force: datetime | None = None):

    assert folder_fullpath.is_absolute() and folder_fullpath.is_dir()

    if file_head_name is None:
        file_head_name = folder_fullpath.name

    if time_force is None:
        time_force = datetime.utcnow()

    time_string = time_force.replace(microsecond=0).isoformat()

    full_filename = folder_fullpath / f'{file_head_name}_{time_string}.fits'
    fits.writeto(str(full_filename), data)  # TODO make headers!


def load_latest_by_folderpath(folder_fullpath: pathlib.Path,
                              file_head_name: str | None = None,
                              to_shm: str | None = None) -> np.ndarray:
    '''
        Will return regardless of setting to SHM or not.
    '''
    assert folder_fullpath.is_absolute() and folder_fullpath.is_dir()

    if file_head_name is None:
        file_head_name = folder_fullpath.name

    most_alph_filename = max(
            glob.glob(str(folder_fullpath / f'{file_head_name}_*.fits')))

    # Check we have a valid datetime?
    _match = re.match(file_head_name + r'_(.*)\.fits',
                      pathlib.Path(most_alph_filename).name)
    assert _match is not None  # or else?
    dt_string = _match.groups()[0]
    dt = datetime.fromisoformat(dt_string)  # this shouldn't raise

    data: np.ndarray = fits.getdata(most_alph_filename)  # type: ignore

    if to_shm is not None:
        shm = SHM(to_shm, data=data)

    return data
