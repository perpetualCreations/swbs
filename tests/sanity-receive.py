"""
proof-of-concept check, receiver
"""

import socket

sock = socket.socket(socket.AF_INET, socket.SOL_SOCKET)
sock.setblocking(True)
print(sock.recvmsg(4096))
