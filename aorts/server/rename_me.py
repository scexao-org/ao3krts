from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

if typ.TYPE_CHECKING:
    from socket import socket

import socketserver

from .tcp_servable import TCPAndMainServable


class ObjectDispatcherServer(socketserver.BaseServer):

    def __init__(self, server_address: str,
                 objs: list[TCPAndMainServable]) -> None:
        super().__init__(server_address, ObjectDispatcherHandler)

        self.registered_objects = {obj.NAME: obj for obj in objs}
        if len(self.registered_objects) < len(objs):
            msg = 'Duplicate key registered to ObjectDispatcherServer.'
            logg.critical(msg)
            raise ValueError(msg)


class ObjectDispatcherHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data: str = self.request.recv(1024).strip().decode()

        data_args = data.split()

        # TODO: catch unknown obj name
        assert isinstance(self.server, ObjectDispatcherServer)  # typeguard

        obj = self.server.registered_objects[data_args[0]]
        answer = obj.tcp_dispatch(data_args[1:])

        self.request.sendall(reply)
