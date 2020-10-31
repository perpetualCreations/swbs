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
