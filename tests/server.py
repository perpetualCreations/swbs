"""
unit test for swbs.Server to swbs.Client
just connects, no other activity
"""

import swbs
import time

server = swbs.Server(42069, b"DOP!DOP!DOP!DOP!")
while True:
    print(server.clients)
    time.sleep(1)
