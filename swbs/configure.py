"""
Socket Wrapper for Byte Strings (SWBS)
Made by perpetualCreations

configure module, configure security keys, hostname and port, and role as client or server.
"""

from swbs import objects

def security(key, hmac_key, auth, hashcompare = False):
    """
    Configures security.
    :param key: encryption key, should be a string and have some degree of entropy.
    :param hmac_key: key for HMAC verification, should be a string and have some degree of entropy.
    :param auth: a password per say, to authenticate hosts, should be a string. if operating as server can be a SHA3 512 hash of auth string or can be just plaintext.
    :param hashcompare: should be a True/False boolean, if operating as server, is auth parameter a hash or plaintext, if False it will be treated as the plaintext version of the auth password, and by default is False.
    :return: None
    """
    objects.keys.key = (objects.MD5.new(key.encode(encoding = "ascii", errors = "replace")).hexdigest()).encode(encoding = "ascii", errors = "replace")
    objects.keys.hmac_key = hmac_key.encode(encoding = "ascii", errors = "replace")
    objects.keys.auth = auth.encode(encoding = "ascii", errors = "replace")
    objects.keys.hashcompare = hashcompare
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

def endpoint(ip = "127.0.0.1", port = 64220, auto = False):
    """
    Configures endpoint host, for operating as a server.
    :param ip: hostname of the endpoint, should be a string. default is localhost or 127.0.0.1. set this to hostname.
    :param port: endpoint port, should be an integer. default is 64220.
    :param auto: True/False boolean, signaling whether to automatically retrieve the hostname, and set it as the IP.
    :return: None
    """
    if auto is True:
        objects.targets.endpoint[0] = objects.socket.gethostname()
    else:
        objects.targets.endpoint[0] = ip
    pass
    objects.targets.endpoint[1] = port
pass

def role(state):
    """
    Configures role as client or server.
    :param state: boolean True/False, if True, signals to operate as server.
    :return: None
    """
    objects.role = state
pass
