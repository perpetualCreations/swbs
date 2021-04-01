"""
SWBS unit test, client script.
"""

import swbs

client = swbs.Client("127.0.0.1", 42069, b"DOP!DOP!DOP!DOP!") # same as other client script, different key
client.connect()
while True:
    client.send(b"Hello world.")
    print(client.receive(return_bytes = True))
