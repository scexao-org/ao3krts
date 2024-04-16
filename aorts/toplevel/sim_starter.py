from __future__ import annotations

import numpy as np
from argparse import ArgumentParser

from multiprocessing import Process

#from pyMilk.interfacing.shm import SHM

from aorts.simtools import analyticalsim as anasim

parser = ArgumentParser(
        prog="aorts_sim",
        description="Basic simulator loop for AO HOWFS/LOWFS/PYWFS")
parser.add_argument('-a', '--apd', action='store_true')
parser.add_argument('-l', '--lowfs', action='store_true')
parser.add_argument('-p', '--pywfs', action='store_true')


# TODO make an entrypoint
def main():
    args = parser.parse_args()

    start_anaytical_sims(args.apd, args.pywfs, args.lowfs)


def start_anaytical_sims(start_apd: bool, start_pywfs: bool, start_lowfs: bool):
    sim_objects: list[anasim.GenericSimulatorObject] = []

    if start_apd:
        ...
        sim_objects.append(sim_mirrors2apd)

    if start_pywfs:
        ...
        sim_objects.append(sim_mirrors2phase)
        sim_objects.append(sim_phase2pywfs)

    if start_lowfs:
        ...
        sim_objects.append(sim_mirrors2lowfs)

    # Do some multiprocessing shenanigans to get everything started...


'''
HOWFS simulator
[dm10disp, dm11disp] -> curv_1kdouble_sim

LOWFS simulator
[dm10disp, dm11disp] -> lowfs_data_sim

PYWFS simulator
[dm10disp, dm11disp] -> bim_phase_sim
bim_phase_sim -> iiwi_sim
'''

if __name__ == "__main__":
    main()
