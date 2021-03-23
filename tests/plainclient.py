"""
unit test for swbs.Client to swbs.Server
just connects, no other activity
"""

import swbs
import time

client = swbs.Client("localhost", 42069, b"DOP!DOP!DOP!DOP!")
client.connect()
time.sleep(5)
client.disconnect()
