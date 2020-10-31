"""
Raspbot Remote Control Application (Raspbot RCA, Raspbot RCA-G), v1.2
swbs module, allows for socket communications.
Made by perpetualCreations

This script handles interfacing functions.
"""

from swbs import objects, acknowledge, exceptions

def encrypt(byte_input):
    """
    Takes byte input and returns encrypted input using a key and encryption nonce.
    :param byte_input: byte string to be encrypted.
    :return: encrypted string, nonce, and HMAC validation.
    """
    if isinstance(byte_input, bytes):
        pass
    else:
        byte_input.encode(encoding = "ascii", errors = "replace")
    pass
    ciphering = objects.Salsa20.new(objects.keys.key)
    encrypted = ciphering.encrypt(byte_input)
    validation = objects.HMAC.new(objects.keys.hmac_key.encode(encoding = "ascii", errors = "replace"), msg = encrypted, digestmod = objects.SHA256)
    return [encrypted, ciphering.nonce, (validation.hexdigest()).encode(encoding = "ascii")]
pass

def decrypt(encrypted_input, validate, nonce):
    """
    Decrypts given encrypted message and validates message with HMAC and nonce from encryption.
    :param encrypted_input: encrypted string to be decrypted.
    :param validate: HMAC validation byte string.
    :param nonce: nonce, additional security feature to prevent replay attacks.
    """
    validation = objects.HMAC.new(objects.keys.hmac_key.encode(encoding = "ascii", errors = "replace"), msg = encrypted_input, digestmod = objects.SHA256)
    try:
        validation.hexverify(validate.decode(encoding = "utf-8", errors = "replace"))
    except ValueError:
        exceptions.HMACMismatch("Failed HMAC validation, disconnected from peer.")
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
    encrypted = encrypt(message)
    objects.socket_send.sendall(encrypted[1] + b" div " + encrypted[2] + b" div " + encrypted[0])
pass

def receive():
    """
    Wrapper for decrypt, formats received input and returns decrypted message. socket.socket_main.recv is now built-in.
    interface.receive has no termination-based method of detecting the end of a message. Instead, it receives 4 bytes,
    This no longer requires to be used as host.receive(self, socket.receive(integer)).
    :return: decrypted message.
    """
    socket_input_spliced = objects.socket_receive.recv(8192).split(b" div ")
    return decrypt(socket_input_spliced[2], socket_input_spliced[1], socket_input_spliced[0])
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
        objects.socket_send.sendall(str(num_id).encode(encoding = "ascii", errors = "replace"))
    else:
        raise exceptions.SentAcknowledgementInvalid("Acknowledgement issued has an invalid ID.")
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
        objects.socket_init.setblocking(True)
        objects.acknowledgement_num_id = int(objects.socket_receive.recv(4).decode(encoding = "utf-8", errors = "replace"))
        objects.socket_init.setblocking(False)
    except objects.socket.error:
        raise objects.socket.error("Raised after SWBS tried to listen on a socket.")
    except ValueError:
        raise ValueError("Acknowledgement could not be decoded from byte string to integer. Unexpected behavior, or packet loss?")
    pass
    try:
        objects.acknowledgement_id = objects.acknowledgement_dictionary[objects.acknowledgement_num_id]
    except KeyError:
        raise KeyError("Acknowledgement could not be decoded from integer to string through the conversion dictionary. Is the peer on a different version, unexpected behavior, or packet loss?")
    pass
    if objects.acknowledgement.num_id in range(0, 2000):
        return True
    else:
        return False
    pass
pass

def connect():
    """
    Connects to pre-configured destination, and starts an encrypted connection.
    :return: None
    """
    try:
        objects.socket_send.connect((objects.targets.destination[0], objects.targets.destination[1]))
    except objects.socket.error:
        raise objects.socket.error("Raised after SWBS tried connecting to the destination host.")
    pass
    interface.send(objects.keys.auth)
    receive_acknowledgement()
pass

def disconnect():
    """
    Sends a message to host notifying that client has disconnected and then closes socket.
    :return: none.
    """
    objects.socket_receive.close(0)
    objects.socket_send.close(0)
pass

def accept():
    """
    Listens for incoming connection requests, and with socket_init creates connection object socket_main.
    This function is blocking, the execution process will halt until a connection is made.
    You may want to run this with multiprocessing.
    :return: None
    """
    objects.socket_connect.bind((objects.targets.endpoint[0], objects.targets.endpoint[1]))
    objects.socket_connect.setblocking(True)
    objects.socket_connect.listen()
    objects.socket_receive, objects.targets.client = objects.socket_connect.accept()
    objects.socket_connect.setblocking(False)
    if (SHA3_512.new(comms.interface.receive()).hexdigest()).encode(encoding = "ascii", errors = "replace") == comms.objects.auth:
        comms.acknowledge.send_acknowledgement(1000)
    else:
        send_acknowledgement(2000)
        raise exceptions.AuthInvalid("Given authentication string was invalid, peer cannot be trusted.")
    pass
pass
