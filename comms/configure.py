"""
Socket Wrapper for Byte Strings (SWBS)
Made by perpetualCreations
"""

from comms import objects

def security(key, hmac_key, auth):
    """
    Configures security.
    :param key: encryption key, should be a string and have some degree of entropy.
    :param hmac_key: key for HMAC verification, should be a string and have some degree of entropy.
    :param auth: a password per say, to authenticate hosts, should be a string.
    :return: None
    """
    objects.key = (objects.MD5.new(key.encode(encoding = "ascii", errors = "replace")).hexdigest()).encode(encoding = "ascii", errors = "replace")
    objects.hmac_key = hmac_key
    objects.auth = auth.encode(encoding = "ascii", errors = "replace")
pass

def destination(ip, port = 64220):
    """
    Configures destination host.
    :param ip: hostname of the destination, should be a string.
    :param port: destination port, should be an integer.
    :return: None
    """
    objects.destination[0] = ip
    objects.destination[1] = port
pass