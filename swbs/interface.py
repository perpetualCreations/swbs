"""
Raspbot Remote Control Application (Raspbot RCA, Raspbot RCA-G), v1.2
swbs module, allows for socket communications.
Made by perpetualCreations

This script handles interfacing functions.
"""

from swbs import objects, errors

def encrypt(byte_input):
    """
    Takes byte input and returns encrypted input using a key and encryption nonce.
    :param byte_input: byte string to be encrypted.
    :return: encrypted string, nonce, and HMAC validation.
    """
    ciphering = objects.Salsa20.new(objects.keys.key)
    encrypted = ciphering.encrypt(byte_input)
    validation = objects.HMAC.new(objects.keys.hmac_key, msg = encrypted, digestmod = objects.SHA256)
    return [encrypted, ciphering.nonce, (validation.hexdigest()).encode(encoding = "ascii")]
pass

def decrypt(encrypted_input, validate, nonce):
    """
    Decrypts given encrypted message and validates message with HMAC and nonce from encryption.
    :param encrypted_input: encrypted string to be decrypted.
    :param validate: HMAC validation byte string.
    :param nonce: nonce, additional security feature to prevent replay attacks.
    """
    validation = objects.HMAC.new(objects.keys.hmac_key, msg = encrypted_input, digestmod = objects.SHA256)
    try:
        validation.hexverify(validate.decode(encoding = "utf-8", errors = "replace"))
    except ValueError:
        errors.HMACMismatch("Failed HMAC validation, disconnected from peer.")
    pass
    ciphering = objects.Salsa20.new(objects.keys.key, nonce = nonce)
    return ciphering.decrypt(encrypted_input)
pass

def send(message):
    """
    Wrapper for encrypt, formats output to be readable for sending, and accesses objects.socket_main to send it.
    This no longer requires to be used as socket.sendall(interface.send(self, b"message")).
    :param message: message to be encrypted.
    :return: None
    """
    if isinstance(message, bytes):
        pass
    elif isinstance(message, str):
        message = message.encode(encoding = "ascii", errors = "replace")
    else:
        message = str(message).encode(encoding = "ascii", errors = "replace")
    pass
    encrypted = encrypt(message)
    if objects.role is True:
        objects.socket_server.sendall((encrypted[1] + b" div " + encrypted[2] + b" div " + encrypted[0]))
    else:
        objects.socket_client.sendall(encrypted[1] + b" div " + encrypted[2] + b" div " + encrypted[0])
    pass
pass

def receive(decode = False):
    """
    Wrapper for decrypt, formats received input and returns decrypted message.
    :param decode: True/False boolean, by default is False, if True will return decoded string instead of bytestring.
    :return: decrypted message.
    """
    if objects.role is True:
        socket_input_spliced = objects.socket_server.recv(8192).split(b" div ")
    else:
        socket_input_spliced = objects.socket_client.recv(8192).split(b" div ")
    pass
    if decode is False:
        return decrypt(socket_input_spliced[2], socket_input_spliced[1], socket_input_spliced[0])
    else:
        return decrypt(socket_input_spliced[2], socket_input_spliced[1], socket_input_spliced[0]).decode(encoding = "utf-8", errors = "replace")
    pass
pass

def send_acknowledgement(num_id):
    """
    Sends an acknowledgement byte string.
    Acknowledgments are used generally for confirming authentication and other specific processes (not general data transmission).

    List of valid IDs:

    ID: 1000
    Alphabetical ID: ok
    Description: General acknowledgement or confirmation.

    ID: 2000
    Alphabetical ID: auth_invalid
    Description: Authentication was invalid, and was rejected by host. Check configuration on both sides to make sure authentication matches.

    ID: 2001
    Alphabetical ID: hmac_fail
    Description: HMAC verification failed. Check configuration on both sides to make sure the key matches.

    :param num_id: ID of acknowledgement to be issued, should be an integer.
    :return: None
    """
    if num_id in list(objects.acknowledgement.dictionary.keys()):
        if objects.role is True:
            objects.socket_server.sendall(str(num_id).encode(encoding = "ascii", errors = "replace"))
        else:
            objects.socket_client.sendall(str(num_id).encode(encoding = "ascii", errors = "replace"))
        pass
    else:
        raise errors.SentAcknowledgementInvalid("Acknowledgement issued has an invalid ID.")
    pass
pass

def receive_acknowledgement():
    """
    Listens for an acknowledgement byte string, returns booleans whether string was received or failed.
    Acknowledgments are used generally for confirming authentication and other specific processes (not general data transmission).

    List of valid IDs:

    ID: 1000
    Alphabetical ID: ok
    Description: General acknowledgement or confirmation.

    ID: 2000
    Alphabetical ID: auth_invalid
    Description: Authentication was invalid, and was rejected by host. Check configuration on both sides to make sure authentication matches.

    ID: 2001
    Alphabetical ID: hmac_fail
    Description: HMAC verification failed. Check configuration on both sides to make sure the key matches.

    :return: True/False boolean, returns False if ID is 2XXX, an error, otherwise returns True.
    """
    try:
        if objects.role is True:
            objects.socket_server.setblocking(True)
            objects.acknowledgement.num_id = int(objects.socket_server.recv(4).decode(encoding = "utf-8", errors = "replace"))
            objects.socket_server.setblocking(False)
        else:
            objects.socket_client.setblocking(True)
            objects.acknowledgement.num_id = int(objects.socket_client.recv(4).decode(encoding = "utf-8", errors = "replace"))
            objects.socket_client.setblocking(False)
        pass
    except ValueError:
        raise ValueError("Acknowledgement could not be decoded from byte string to integer. Unexpected behavior, or packet loss?")
    pass
    try:
        objects.acknowledgement.id = objects.acknowledgement.dictionary[objects.acknowledgement.num_id]
    except KeyError:
        raise KeyError("Acknowledgement could not be decoded from integer to string through the conversion dictionary. Is the peer on a different version, unexpected behavior, or packet loss?")
    pass
    if objects.acknowledgement.num_id in range(0, 2000):
        return True
    elif objects.acknowledgement.num_id == 2000:
        raise errors.AuthInvalid("Given authentication string was invalid, this host was not trusted.")
    else:
        return False
    pass
pass

def connect():
    """
    Connects to pre-configured destination, and starts an encrypted connection.
    :return: None
    """
    if objects.role is True:
        raise errors.NotClient("interface.connect was invoked, while running as server.")
    pass
    objects.socket_client.connect((objects.targets.destination[0], objects.targets.destination[1]))
    send(objects.keys.auth)
    receive_acknowledgement()
pass

def disconnect():
    """
    Closes active socket.
    :return: None
    """
    if objects.role is True:
        try:
            objects.socket_server.close()
        except objects.socket.error:
            pass
        pass
        objects.socket_server = objects.socket.socket(objects.socket.AF_INET, objects.socket.SOCK_STREAM)
    else:
        try:
            objects.socket_client.close()
        except objects.socket.error:
            pass
        pass
        objects.socket_client = objects.socket.socket(objects.socket.AF_INET, objects.socket.SOCK_STREAM)
    pass
pass

def accept():
    """
    Listens for incoming connection requests, and with socket_init creates connection object socket_main.
    This function is blocking, the execution process will halt until a connection is made.
    You may want to run this with multiprocessing.
    :return: None
    """
    if objects.role is False:
        raise errors.NotServer("interface.accept was invoked, while running as client.")
    pass
    objects.socket_connect.bind((objects.targets.endpoint[0], objects.targets.endpoint[1]))
    objects.socket_connect.setblocking(True)
    objects.socket_connect.listen()
    objects.socket_server, objects.targets.client = objects.socket_connect.accept()
    objects.socket_connect.setblocking(False)
    if objects.keys.hashcompare is False:
        if receive() == objects.keys.auth:
            send_acknowledgement(1000)
        else:
            send_acknowledgement(2000)
            raise errors.AuthInvalid("Given authentication string was invalid, peer cannot be trusted.")
        pass
    else:
        if (objects.SHA3_512.new(receive()).hexdigest()).decode(encoding = "ascii", errors = "replace") == objects.keys.auth:
            send_acknowledgement(1000)
        else:
            send_acknowledgement(2000)
            raise errors.AuthInvalid("Given authentication string was invalid, peer cannot be trusted.")
        pass
    pass
pass
