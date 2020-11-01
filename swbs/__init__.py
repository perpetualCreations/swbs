"""
Socket Wrapper for Byte Strings (SWBS)
Made by perpetualCreations
"""

print("[INFO]: Initiating swbs module...")

from swbs import configure, exceptions, interface, objects

objects.socket_client = objects.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
objects.socket_client.setblocking(False)
objects.socket_client.settimeout(10)

objects.socket_server = None

objects.socket_connect = objects.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
objects.socket_connect.setblocking(False)
objects.socket_connect.settimeout(5)
