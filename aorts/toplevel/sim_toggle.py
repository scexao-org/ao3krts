from __future__ import annotations

import typing as typ

import os
import re
import pathlib
import logging

logg = logging.getLogger(__name__)

from swmain.infra.logger import init_logger_autoname

from .. import config
from ..cacao_stuff.loop_manager import CacaoConfigReader

MILK_SHM_DIR: str = os.environ['MILK_SHM_DIR']
STREAMNAME_FORMATTER = MILK_SHM_DIR + '/%s.im.shm'

SYMLINK_TARGET: dict[str, tuple[str, str]] = {
        # Link | Real | Sim
        # Inputs
        f'aol{config.LOOPNUM_HOAPD_BIM188}_wfsim':
                ('curv_1kdouble', 'curv_1kdouble_sim'
                 ),  # TODO other curv computations
        f'aol{config.LOOPNUM_LOAPD_BIM188}_wfsim':
                ('lowfs_data', 'lowfs_data_sim'),
        f'aol{config.LOOPNUM_IRPYR_BIM188}_wfsim': ('iiwi', 'iiwi_sim'),
        f'aol{config.LOOPNUM_BIM2TTOFFLOAD}_wfsim':
                (f'dm{config.DMNUM_BIM188}disp',
                 f'dm{config.DMNUM_BIM188SIM}disp'),
}


def find_chan_dm_numbers(dm_shm_file: pathlib.Path | str) -> tuple[str, str]:
    '''
        Extract XX and YY from /milk/shm/dmXXdispYY.im.shm
    '''
    if isinstance(dm_shm_file, str):
        dm_shm_file = pathlib.Path(dm_shm_file)

    dmXXdispYY = dm_shm_file.name
    assert dmXXdispYY.endswith('.im.shm')
    dmXXdispYY = dmXXdispYY.removesuffix('.im.shm')

    dm_num, channel_num = re.match('dm(\d+)disp(\d+)', dmXXdispYY).groups()

    return dm_num, channel_num


def reconf_dm_pointing_symlink(link: str, target_dm: str) -> None:
    _, chfound = find_chan_dm_numbers(os.readlink(link))
    reconf_shm_symlink(link, f'dm{target_dm}disp{chfound}')


def reconf_shm_symlink(link: str, targetfile: str) -> None:
    try:
        os.symlink(STREAMNAME_FORMATTER % targetfile,
                   STREAMNAME_FORMATTER % link)
    except OSError:  # ln -sf
        os.remove(link)
        os.symlink(STREAMNAME_FORMATTER % targetfile,
                   STREAMNAME_FORMATTER % link)


def toggle_sim_dmoutputs_by_loopnumber(loop_number: int,
                                       dm_number_as_str: str) -> None:

    # Make a string formatter for /milk/shm/aolX_%s.im.shm
    this_loop_formatter = STREAMNAME_FORMATTER % f'aol{loop_number}_%s'

    reconf_dm_pointing_symlink(this_loop_formatter % 'dmC', dm_number_as_str)
    reconf_dm_pointing_symlink(this_loop_formatter % 'dmdisp', dm_number_as_str)
    reconf_dm_pointing_symlink(this_loop_formatter % 'dmRM', dm_number_as_str)
    # TODO: there's a bit more of those but they're significantly not used as much


def toggle_simulator(on_off: bool) -> None:
    '''
        Toggle symlinks all around to make sure we're running all on simulated SHMs
    '''
    for link, targets in SYMLINK_TARGET.values():

        target = targets[on_off]

        if not os.path.islink(STREAMNAME_FORMATTER % link):
            # FIXME check who's pointing to what... unclear in the DM space at all.
            err_msg = f"{link} is expected be a simlink."
            logg.critical(err_msg)
            raise ValueError(err_msg)

        reconf_shm_symlink(link, target)

    bim_number = (config.DMNUM_BIM188, config.DMNUM_BIM188SIM)[on_off]
    tt_number = (config.DMNUM_TT, config.DMNUM_TTSIM)[on_off]

    toggle_sim_dmoutputs_by_loopnumber(config.LOOPNUM_HOAPD_BIM188, bim_number)
    toggle_sim_dmoutputs_by_loopnumber(config.LOOPNUM_LOAPD_BIM188, bim_number)
    toggle_sim_dmoutputs_by_loopnumber(config.LOOPNUM_IRPYR_BIM188, bim_number)
    toggle_sim_dmoutputs_by_loopnumber(config.LOOPNUM_BIM2TTOFFLOAD, tt_number)


# Todo - clickify, pyproject entrypoint
def toggle_simulator_main(*args, **kwargs):
    pass
