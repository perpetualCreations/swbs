"""
SWBS unit test, server script
"""

import swbs

host = swbs.Host(42069, b"AoAoAoAoAoAoAoAo")
host.listen()
print(host.receive())
host.send("Something silly.")
host.disconnect()
