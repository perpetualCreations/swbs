"""
Socket Wrapper for Byte Strings (SWBS)
Made by perpetualCreations

configure module, configure security keys, hostname and port, and role as client or server.
"""

from swbs import objects

def security(key, hmac_key, auth):
    """
    Configures security.
    :param key: encryption key, should be a string and have some degree of entropy.
    :param hmac_key: key for HMAC verification, should be a string and have some degree of entropy.
    :param auth: a password per say, to authenticate hosts, should be a string.
    :return: None
    """
    objects.keys.key = (objects.MD5.new(key.encode(encoding = "ascii", errors = "replace")).hexdigest()).encode(encoding = "ascii", errors = "replace")
    objects.keys.hmac_key = hmac_key
    objects.keys.auth = auth.encode(encoding = "ascii", errors = "replace")
pass

def destination(ip, port = 64220):
    """
    Configures destination host, for operating as a client.
    :param ip: hostname of the destination, should be a string. default is 64220.
    :param port: destination port, should be an integer.
    :return: None
    """
    objects.targets.destination[0] = ip
    objects.targets.destination[1] = port
pass

def endpoint(ip = "127.0.0.1", port = 64220):
    """
    Configures endpoint host, for operating as a server.
    :param ip: hostname of the endpoint, should be a string. default is localhost or 127.0.0.1, this should not be changed.
    :param port: endpoint port, should be an integer. default is 64220.
    :return: None
    """
    objects.targets.endpoint[0] = ip
    objects.targets.endpoint[1] = port
pass

def role(state = False):
    """
    Configures role as client or server.
    :param state: boolean True/False, if True, signals to operate as server.
    :return: None
    """
    objects.role = state
pass
