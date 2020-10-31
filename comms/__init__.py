"""
Socket Wrapper for Byte Strings (SWBS)
Made by perpetualCreations
"""

print("[INFO]: Initiating comms module...")

from comms import interface, connect, disconnect, acknowledge, objects

objects.exchange = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
objects.exchange.setblocking(False)
objects.exchange.settimeout(10)
