"""
SWBS unit test, client script.
"""

import swbs

swbs.configure.security("somekey", "anotherkey", "somanykeys")
swbs.configure.role(False)
swbs.configure.destination("localhost")
swbs.interface.connect()
swbs.interface.send("testing testing, 1, 2, 3.")
