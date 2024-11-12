from __future__ import annotations

# Typing
import typing as typ

from ..datafinder import RTMDataSupervisor

# Stock external
import abc
import numpy as np

# Homemade external
from pyMilk.interfacing.shm import SHM
from pyMilk.interfacing.fps import FPS

# Internal


class TopicFetcher(typ.Protocol):

    @abc.abstractmethod
    def __init__(self, data_vault: RTMDataSupervisor, *args, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def fetch(self, *args, **kwargs) -> None:
        pass


class FPSFetcher(TopicFetcher):

    def __init__(self, data_vault: RTMDataSupervisor, fps_name: str,
                 topics: typ.Dict[str, typ.Any]) -> None:
        self.fps = FPS(fps_name)
        # TODO? some internal statuses to fetch if exists, autorelink, tmux alive, conf alive,

        self.topics = topics

        self.data_vault = data_vault

    def fetch(self):
        for datavault_key, fps_key in self.topics.values():
            self.data_vault[datavault_key] = self.fps.get_param(fps_key)


class SHMFetcher(TopicFetcher):

    def __init__(
            self,
            data_vault: RTMDataSupervisor,
            data_name: str,
            shm_name: str,
            shm_callables: typ.Dict[str, typ.Callable[[SHM], typ.Any]] = {},
            data_callables: typ.Dict[str, typ.Callable[[np.ndarray],
                                                       typ.Any]] = {},
    ) -> None:

        # TODO? AUTORELINK! Actually SHM owners may re-create it entirely.

        self.data_vault = data_vault
        self.data_name = data_name

        self.shm_name = shm_name
        self.shm = SHM(shm_name)

        self.shm_callables = shm_callables
        self.data_callables = data_callables

    def fetch(self) -> None:
        for var_name, callable in self.shm_callables.items():
            self.data_vault[var_name] = callable(self.shm)

        self.data = self.shm.get_data(False, copy=True)
        self.data_vault[self.data_name] = self.data  # Ideally, no copy.

        for var_name, callable in self.data_callables.items():
            self.data_vault[var_name] = callable(self.data)


class APD2DFetcher(SHMFetcher):

    def fetch(self) -> None:
        for var_name, callable in self.shm_callables.items():
            self.data_vault[var_name] = callable(self.shm)

        self.curv_index: int = self.shm.get_keywords()[
                '_CURV_SGN']  # TODO: config.

        self.data = self.shm.get_data(False, copy=True)[self.curv_index, :]
        self.data_vault[self.data_name] = self.data  # Ideally, no copy.

        for var_name, callable in self.data_callables.items():
            self.data_vault[var_name] = callable(self.data)
