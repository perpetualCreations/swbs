"""
Raspbot Remote Control Application (Raspbot RCA, Raspbot RCA-G), v1.2
swbs module, allows for socket communications.
Made by perpetualCreations

Contains objects for module, including any package imports. Interact with these objects through swbs.objects.
"""

import socket
from Cryptodome.Cipher import Salsa20
from Cryptodome.Hash import HMAC, SHA256, MD5, SHA3_512

socket_server = None # socket object placeholder
socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

socket_client.setblocking(False)
socket_client.settimeout(10)

socket_connect.setblocking(False)
socket_connect.settimeout(10)

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
    hashcompare = False
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
