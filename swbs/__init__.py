"""
Socket Wrapper for Byte Strings (SWBS)
Made by perpetualCreations
"""

import socket
from Cryptodome.Cipher import AES
from Cryptodome.Hash import MD5
from typing import Union
from os import urandom

# TODO setup this module to accept multiple clients for one server on a single port

class Exceptions:
    """
    Parent class for child classes serving as exceptions deriving from BaseException.
    """
    class SecurityError(BaseException):
        """
        Exception raised by Security class.
        """
    class InterfaceError(BaseException):
        """
        Exception raised by Interface class.
        """
    class ServerError(BaseException):
        """
        Exception raised by Server class instance.
        """
    class ClientError(BaseException):
        """
        Exception raised by Client class instance.
        """

class Interface:
    """
    Interfacing wrapper. Contains static functions for sending and receiving messages.
    Use a Server or Client class instance to access these functions.
    """
    @staticmethod
    def send(socket_instance: object, key: bytes, message: Union[str, bytes]) -> None:
        """
        Uses Security class to encrypt a message, sends encrypted message with provided socket object.

        :param socket_instance: object, socket object
        :param key: bytes, AES encryption key to be passed off to Security.encrypt
        :param message: Union[str, bytes], message for sending and encrypting
        :return: None
        """
        components = Security.encrypt(key, message)
        socket_instance.setblocking(True)
        try: socket_instance.sendall(components[0] + b" |div| " + components[1] + b" |div| " + components[2])
        except socket.error as ParentException:
            socket_instance.setblocking(False)
            raise Exceptions.InterfaceError("Failed to send message.") from ParentException
        socket_instance.setblocking(False)

    @staticmethod
    def receive(socket_instance: object, key: bytes, buffer_size: int = 4096) -> str:
        """
        Uses Security class to decrypt a received message, returns message as string.

        :param socket_instance: object, socket object
        :param key: bytes, AES encryption key to be passed off to Security.decrypt
        :param buffer_size: int, size of receiving buffer, default 4096
        :return: str, decrypted message received
        """
        try:
            socket_instance.setblocking(True)
            components = socket_instance.recv(buffer_size).split(b" |div| ")
        except socket.error as ParentException:
            socket_instance.setblocking(False)
            raise Exceptions.InterfaceError("Failed to receive message.") from ParentException
        socket_instance.setblocking(False)
        return Security.decrypt(key, components[0], components[1], components[2])

class Security:
    """
    AES security wrapper. Contains security-related static functions.
    """
    @staticmethod
    def generate_key(dump_to_path: Union[str, None] = None, random_max: int = 1024, random_min: int = 16) -> Union[bytes, None]:
        """
        Generates a random 16-byte AES key bytestring, by creating a random string of characters, length between random_max and random_min, and hashing the string.
        Generated key can be returned or written to a file.

        :param dump_to_path: Union[str, None], if provided string, parameter is interpreted as path to a file for key to be written to, otherwise key is returned, default None
        :param random_max: int, maximum random character length for key generation through hashing, default 1024
        :param random_min: int, minimum random character length for key generation through hashing, default 16
        :return: Union[bytes, None], if dump_to_path is not string, return bytes being the key, otherwise return None
        """
        assert random_min <= random_max, "random_min is greater than random_max."
        assert random_min > 0, "random_min is or is less than 0."
        if isinstance(dump_to_path, str) is True:
            with open(dump_to_path, "wb") as key_dump: key_dump.write(MD5.new(urandom(randrange(random_min, random_max))).hexdigest().encode("ascii"))
        else: return MD5.new(urandom(randrange(random_min, random_max))).hexdigest().encode("ascii")

    @staticmethod
    def get_key(key: Union[str, bytes], key_is_path: bool = False) -> bytes:
        """
        Collects key, if already bytes and not from path, returns bytes again.

        :param key: Union[str, bytes], if key_is_path is False, key string, otherwise path to key file
        :param key_is_path: bool, if True, key parameter is treated as path to key file for reading from, default False
        :return: bytes, encryption key
        """
        if key_is_path is True:
            try:
                with open(key, "rb") as key_handle: key = key_handle.read()
            except FileNotFoundError as ParentException: raise Exceptions.SecurityError("Key file does not exist.") from ParentException
        if isinstance(key, str): key = key.encode("ascii", "replace")
        if len(key) != 16: raise Exceptions.SecurityError("Key length is not 16, cannot be used for AES encryption.")
        return key

    @staticmethod
    def encrypt(key: Union[str, bytes], message: Union[str, bytes]) -> list:
        """
        Encrypts a string with a 16-byte key for AES, returns encrypted contents.

        :param key: Union[str, bytes], AES encryption key
        :param message: Union[str, bytes], message for encryption
        :return: list, [encrypted message, tag, nonce]
        """
        if isinstance(message, str): message = message.encode("ascii", "replace")
        if isinstance(key, str): key = key.encode("ascii")
        encryptor = AES.new(key, AES.MODE_EAX)
        encrypted, tag = encryptor.encrypt_and_digest(message)
        return [encrypted, tag, encryptor.nonce]

    @staticmethod
    def decrypt(key: Union[str, bytes], message: bytes, tag: bytes, nonce: bytes) -> str:
        """
        Decrypts a string with a 16-byte key for AES, tag, and nonce, returns decrypted string.

        :param key: Union[str, bytes], AES encryption key
        :param message: bytes, message for decryption
        :param tag: bytes, encryption tag
        :param nonce: bytes, encryption nonce
        :return: str, decrypted string
        """
        try:
            if isinstance(key, str): key = key.encode("ascii")
            return AES.new(key, AES.MODE_EAX, nonce).decrypt_and_verify(message, tag).decode("utf-8", "replace")
        except ValueError as ParentException: raise Exceptions.SecurityError("Message integrity verification failed.") from ParentException

class Instance:
    """
    Socket wrapper factory.
    """
    def __init__(self, port: int, key: Union[str, bytes], host: str = "localhost", key_is_path: bool = False):
        """
        Creates class socket object with supplied host and port for binding.

        :param port: int, port to bind to
        :param key: see Security.get_key for parameter documentation
        :param host: str, hostname to bind to, auto-filled in by socket.gethostname()
        :param key_is_path: see Security.get_key for parameter documentation
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Instance.set_timeout(self, 5)
        Instance.set_blocking(self, True)
        try:
            self.socket.bind((host, port))
        except socket.error: Instance.restart(self)
        self.key = Security.get_key(key, key_is_path)

    def set_blocking(self, state: bool) -> None:
        """
        Set instance's socket to be blocking or not blocking.
        Non-blocking operation will cause SocketError No. 10035.

        :param state: bool, whether socket should be blocking
        :return: None
        """
        self.socket.setblocking(state)

    def set_timeout(self, time: int) -> None:
        """
        Set instance's socket's seconds until timeout.

        :param time: int, seconds until timeout
        :return: None
        """
        self.socket.settimeout(time)

    def send(self, message) -> None:
        """
        See Interface.send for documentation.

        :param message: message to be sent.
        :return: None
        """
        Interface.send(self.socket, self.key, message)

    def receive(self) -> str:
        """
        See Interface.receive for documentation.

        :return: str, message received
        """
        return Interface.receive(self.socket, self.key)

    def close(self) -> None:
        """
        Closes Instance socket. If applicable, effectively closes connections.

        :return: None
        """
        self.socket.close()

    def restart(self) -> None:
        """
        Closes and reopens Instance socket. If applicable, effectively closes connections, like Instance.close.

        :return: None
        """
        try: Instance.close(self)
        except socket.error: pass
        except AttributeError: pass
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

class Host(Instance):
    """
    Host socket wrapper, derived from Instance. Factory method.
    """
    def __init__(self, port: int, key: Union[str, bytes], host: str = "localhost", key_is_path: bool = False):
        """
        Initialize instance. See documentation for Instance.
        """
        super().__init__(port, key, host, key_is_path)
        self.client_address = None

    def listen(self) -> None:
        """
        Starts listening for connections.

        :return: None
        """
        Instance.set_blocking(self, True)
        self.socket.listen()
        self.socket, self.client_address = self.socket.accept()
        Instance.set_blocking(self, False)

    def disconnect(self) -> None:
        """
        Calls Instance.restart, exists to support semantics.

        :return: None
        """
        Instance.restart(self)

class Client(Instance):
    """
    Client socket wrapper, derived from Instance. Factory method.
    """
    def __init__(self, host: str, port: int, key: Union[str, bytes], key_is_path: bool = False):
        """
        Initialize instance.

        :param host: str, hostname of host to connect to
        :param port: int, port that host is listening on
        :param key: see Instance documentation
        :param key_is_path: see Instance documentation
        """
        super().__init__(port, key, "localhost", key_is_path)
        del self.socket
        Instance.restart(self)
        self.host = host
        self.port = port

    def connect(self) -> None:
        """
        Starts listening for connections.

        :return: None
        """
        Instance.set_blocking(self, True)
        self.socket.connect((self.host, self.port))
        Instance.set_blocking(self, False)

    def disconnect(self) -> None:
        """
        Calls Instance.restart, exists to support semantics.

        :return: None
        """
        Instance.restart(self)
