# -*- coding: utf-8 -*-
import socket
from enum import Enum
from json import dumps, loads
from struct import pack, unpack
import time

SERVER = 'wgforge-srv.wargaming.net'
PORT = 443


class Action(Enum):
    LOGIN = 1
    LOGOUT = 2
    MOVE = 3
    UPGRADE = 4
    TURN = 5
    PLAYER = 6
    MAP = 10


class Result(Enum):
    OKEY = 0
    BAD_COMMAND = 1
    RESOURCE_NOT_FOUND = 2
    ACCESS_DENIED = 3
    NOT_READY = 4
    TIMEOUT = 5
    INTERNAL_SERVER_ERROR = 500


class ServerConnection:
    def __init__(self, server, port):
        self.__socket = socket.socket()
        self.__socket.connect((server, port))

    def __request(self, action, data=None):
        if data:
            msg = pack('ii', action.value, len(data)) + data.encode('UTF-8')
        else:
            msg = pack('ii', action.value, 0)
        self.__socket.send(msg)

    def __response(self):
        res = unpack('i', self.__socket.recv(4))[0]
        if res == 0:
            size = unpack('i', self.__socket.recv(4))[0]
            if size:
                data = b''
                while size > 128:
                    data += self.__socket.recv(128)
                    size -= 128
                data += self.__socket.recv(size)
                return loads(data.decode('UTF-8'))
        return res
