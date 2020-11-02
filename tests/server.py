"""
SWBS unit test, server script
"""

import swbs

swbs.configure.role(True)
swbs.configure.security("somekey", "anotherkey", "somanykeys")
swbs.interface.accept()
print(swbs.interface.receive(True))
