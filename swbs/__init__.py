"""
Socket Wrapper for Byte Strings (SWBS)
Made by perpetualCreations
"""

print("[INFO]: Initiating swbs module...")

from swbs import interface, connect, disconnect, acknowledge, objects

objects.socket_send = objects.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
objects.socket_send.setblocking(False)
objects.socket_send.settimeout(10)

objects.socket_receive = None

objects.socket_connect = objects.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
objects.socket_connect.setblocking(False)
objects.socket_connect.settimeout(5)

