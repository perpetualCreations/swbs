"""
SWBS unit test, client script.
"""

import swbs

client = swbs.Client("127.0.0.1", 42069, b"AoAoAoAoAoAoAoAo")
client.connect()
client.send(b"Hello world.")
print(client.receive())
client.disconnect()
