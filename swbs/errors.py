"""
Socket Wrapper for Byte Strings (SWBS)
Made by perpetualCreations

exceptions module, contains swbs exceptions raised at errors.
"""

from swbs import interface

class AuthInvalid(Exception):
    """
    Authentication string provided was invalid.
    """
    interface.disconnect()
pass

class HMACMismatch(Exception):
    """
    HMAC verification failed.
    This usually is indicative of an invalid key, an erroneous message, or an actual attack.
    """
    interface.disconnect()
pass

class SentAcknowledgementInvalid(Exception):
    """
    interface.send_acknowledgement was given an invalid acknowledgement ID.
    """
pass

class ReceivedAcknowledgementInvalid(Exception):
    """
    interface.receive_acknowledgement received an invalid acknowledgement ID.
    """
pass

class NotClient(Exception):
    """
    A function was invoked that was not intended to be ran by the host running as a server.
    """
pass

class NotServer(Exception):
    """
    A function was invoked that was not intended to be ran by the host running as a client.
    """
pass
