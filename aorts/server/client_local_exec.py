from __future__ import annotations

import typing as typ

import sys

import click

from .server_main import CMD_OBJS


@click.command
@click.argument('obj_name', type=click.Choice(list(CMD_OBJS.keys())))
@click.argument('all_else', nargs=-1)
def rts23_localexec(obj_name: str, all_else: list[str]):

    command_obj_to_call = CMD_OBJS[obj_name]

    print(command_obj_to_call.DISPATCHER.click_dispatch_cli_calls(all_else))
