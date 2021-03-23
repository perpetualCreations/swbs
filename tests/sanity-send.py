"""
proof-of-concept check, sender
"""

import socket

sock = socket.socket(socket.AF_UNIX, socket.SOL_SOCKET)
sock.setblocking(True)
sock.sendmsg(b"Hello world.",__address="127.0.0.1")
