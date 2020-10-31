"""
Raspbot Remote Control Application (Raspbot RCA, Raspbot RCA-G), v1.2
comms module, allows for socket communications.
Made by perpetualCreations

This script handles interfacing functions.
"""

from comms import objects, disconnect, acknowledge

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
    ciphering = objects.Salsa20.new(objects.key)
    encrypted = ciphering.encrypt(byte_input)
    validation = objects.HMAC.new(objects.hmac_key.encode(encoding = "ascii", errors = "replace"), msg = encrypted, digestmod = objects.SHA256)
    return [encrypted, ciphering.nonce, (validation.hexdigest()).encode(encoding = "ascii")]
pass

def decrypt(encrypted_input, validate, nonce):
    """
    Decrypts given encrypted message and validates message with HMAC and nonce from encryption.
    :param encrypted_input: encrypted string to be decrypted.
    :param validate: HMAC validation byte string.
    :param nonce: nonce, additional security feature to prevent replay attacks.
    """
    validation = objects.HMAC.new(objects.hmac_key.encode(encoding = "ascii", errors = "replace"), msg = encrypted_input, digestmod = objects.SHA256)
    try:
        validation.hexverify(validate.decode(encoding = "utf-8", errors = "replace"))
    except ValueError:
        disconnect.disconnect()
        print("[FAIL]: Message is not authentic, failed HMAC validation!")
    pass
    ciphering = objects.Salsa20.new(objects.key, nonce = nonce)
    return ciphering.decrypt(encrypted_input)
pass

def send(message):
    """
    Wrapper for encrypt, formats output to be readable for sending, and accesses objects.socket_main to send it.
    This no longer requires to be used as socket.sendall(interface.send(self, b"message")).
    :param message: message to be encrypted.
    :return: none
    """
    encrypted = encrypt(message)
    objects.socket_main.sendall(encrypted[1] + b" div " + encrypted[2] + b" div " + encrypted[0])
pass

def receive():
    """
    Wrapper for decrypt, formats received input and returns decrypted message. socket.socket_main.recv is now built-in.
    interface.receive has no termination-based method of detecting the end of a message. Instead, it receives 4 bytes,
    This no longer requires to be used as host.receive(self, socket.receive(integer)).
    :return: decrypted message.
    """
    socket_input_spliced = objects.socket_main.recv(8192).split(b" div ")
    return decrypt(socket_input_spliced[2], socket_input_spliced[1], socket_input_spliced[0])
pass
