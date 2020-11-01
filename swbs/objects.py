"""
Raspbot Remote Control Application (Raspbot RCA, Raspbot RCA-G), v1.2
swbs module, allows for socket communications.
Made by perpetualCreations

Contains objects for module, including any package imports. Interact with these objects through swbs.objects.
"""

try:
    import socket
    from platform import system
    from subprocess import call, Popen
    from time import sleep
    from Cryptodome.Cipher import Salsa20
    from Cryptodome.Hash import HMAC, SHA256, MD5
    from ast import literal_eval
    from os import getcwd
    from basics import basics, process # TODO review usage
except ImportError as ImportErrorMessage:
    raise ImportError("Raised after SWBS tried importing modules.")
except ImportWarning as ImportWarningMessage:
    raise ImportWarning("Raised after SWBS tried importing modules.")
pass

socket_server = None # socket object placeholder
socket_client = None # socket object placeholder
socket_connect = None # socket connection object placeholder

role = False

class keys:
    """
    Class containing security keys.

    :var key: Salsa20 encryption key, by default None, otherwise a string if configured
    :var hmac_key: HMAC key, by default None, otherwise a string if configured
    :var auth: authentication key, by default None, otherwise a string if configured
    """
    key = None
    hmac_key = None
    auth = None
pass

class targets:
    """
    Class containing hostname and port of the destination and endpoint.
    The respective information is labeled as such, formatted as [hostname, port].

    :var destination: list containing host and port of destination.
    :var endpoint: list containing host and port of endpoint.
    :var client: string containing the address of the client.
    """
    destination = [None, 64220]
    endpoint = ["127.0.0.1", 64220]
    client = None
pass

class acknowledgement:
    """
    Class containing dictionary, ID, and numeric ID, for acknowledgements.

    :var dictionary: dictionary for look ups, to convert numeric ID codes to readable alphabetical IDs
    :var id: placeholder, will be overwritten by lookup with acknowledgement_dictionary
    :var num_id: placeholder, will be overwritten by receiving socket input
    """
    dictionary = {1000:"ok", 2000:"auth_invalid", 2001:"hmac_fail"}
    id = None
    num_id = None
pass
