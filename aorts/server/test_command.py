from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

from .dispatcher import ClickDispatcher, ClickRemotelyInvokableObject

import click


class ActualInterestingTestObject(ClickRemotelyInvokableObject):

    NAME = 'TEST'
    DESCR = 'Test Object'

    DISPATCHER = ClickDispatcher(click_group=NAME)

    @DISPATCHER.click_invokator.command('efgh')
    @click.argument('x', type=int)
    @click.pass_obj
    def efgh(self, x: int) -> str:
        return f'efgh: {x} -> {x+1}'
