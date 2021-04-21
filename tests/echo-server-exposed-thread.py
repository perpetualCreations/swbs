"""
unit test for swbs.Server to swbs.Client
echoes received buffer to client

testing exposed instances
"""

import swbs
from typing import Union
import socket
from time import sleep


class Echo(swbs.ServerClientManagers.ClientManagerInstanceExposed):
    def __init__(self, instance, connection_socket: Union[socket.socket, object], client_id: int) -> None:
        """
        Sends received bytes back to client, hence, producing an ECHO.
        Has similar behavior with ServerClientManagers.client_manager in which it will close the connection instance
        alongside client disconnect.

        :param instance: class instance
        :param connection_socket: Union[socket.socket, object], socket object from connection
        :param client_id: int, client identification
        :return: None
        """
        super().__init__(instance, connection_socket, client_id)

    def run(self):
        while True:
            sleep(1)
            # noinspection PyBroadException
            try:
                swbs.Instance.send(self.instance, swbs.Instance.receive(self.instance,
                                                                        socket_instance=self.connection_socket),
                                   self.connection_socket)
            except BaseException:
                del self.instance.clients[self.client_id]
                break


server = swbs.Server(42069, b"DOP!DOP!DOP!DOP!", connection_handler=Echo)
while True:
    print(server.clients)
    try:
        # when at least one client is connected, should print 0
        print(server.clients[0]["thread"].client_id)
    except Exception:
        pass
    sleep(1)
