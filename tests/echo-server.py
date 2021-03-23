"""
unit test for swbs.Server to swbs.Client
echoes received buffer to client
"""

import swbs
import time

server = swbs.Server(42069, b"DOP!DOP!DOP!DOP!", connection_handler = swbs.ServerClientManagers.echo)
while True:
    print(server.clients)
    time.sleep(1)
