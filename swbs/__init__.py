"""
Socket Wrapper for Byte Strings (SWBS)
Made by perpetualCreations
"""

import socket
import threading
from Cryptodome.Cipher import AES
from Cryptodome.Hash import MD5
from typing import Union
from os import urandom
from time import sleep
from random import randint


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


class Security:
    """
    AES security wrapper. Contains security-related static functions.
    """

    @staticmethod
    def generate_key(dump_to_path: Union[str, None] = None, random_max: int = 1024, random_min: int = 16) -> \
            Union[bytes, None]:
        """
        Generates a random 16-byte AES key bytestring, by creating a random string of characters, length between
        random_max and random_min, and hashing the string. Generated key can be returned or written to a file.

        :param dump_to_path: Union[str, None], if provided string, parameter is interpreted as path to a file for key
            to be written to, otherwise key is returned, default None
        :param random_max: int, maximum random character length for key generation through hashing, default 1024
        :param random_min: int, minimum random character length for key generation through hashing, default 16
        :return: Union[bytes, None], if dump_to_path is not string, return bytes being the key, otherwise return None
        """
        assert random_min <= random_max, "random_min is greater than random_max."
        assert random_min > 0, "random_min is or is less than 0."
        if isinstance(dump_to_path, str) is True:
            with open(dump_to_path, "wb") as key_dump:
                key_dump.write(MD5.new(urandom(randint(random_min, random_max))).hexdigest().encode("ascii"))
        else:
            return MD5.new(urandom(randint(random_min, random_max))).hexdigest().encode("ascii")

    @staticmethod
    def get_key(key: Union[str, bytes, None], key_is_path: bool = False) -> Union[bytes, None]:
        """
        Collects key, if already bytes and not from path, returns bytes again.

        :param key: Union[str, bytes, None], if key_is_path is False, key string, otherwise path to key file, if None
            return None
        :param key_is_path: bool, if True, key parameter is treated as path to key file for reading from, default False
        :return: bytes, encryption key
        """
        if key is None:
            return None
        if key_is_path is True:
            try:
                with open(key, "rb") as key_handle:
                    key = key_handle.read()
            except FileNotFoundError as ParentException:
                raise Exceptions.SecurityError("Key file does not exist.") from ParentException
        if isinstance(key, str):
            key = key.encode("ascii", "replace")
        if len(key) != 16:
            raise Exceptions.SecurityError("Key length is not 16, cannot be used for AES encryption.")
        return key

    @staticmethod
    def encrypt(key: Union[str, bytes], message: Union[str, bytes]) -> list:
        """
        Encrypts a string with a 16-byte key for AES, returns encrypted contents.

        :param key: Union[str, bytes], AES encryption key
        :param message: Union[str, bytes], message for encryption
        :return: list, [encrypted message, tag, nonce]
        """
        if isinstance(message, str):
            message = message.encode("ascii", "replace")
        if isinstance(key, str):
            key = key.encode("ascii")
        encryptor = AES.new(key, AES.MODE_EAX)
        encrypted, tag = encryptor.encrypt_and_digest(message)
        return [encrypted, tag, encryptor.nonce]

    @staticmethod
    def decrypt(key: Union[str, bytes], message: bytes, tag: bytes, nonce: bytes, return_bytes: bool = False) -> \
            Union[str, bytes]:
        """
        Decrypts a string with a 16-byte key for AES, tag, and nonce, returns decrypted string or bytes, default string.

        :param key: Union[str, bytes], AES encryption key
        :param message: bytes, message for decryption
        :param tag: bytes, encryption tag
        :param nonce: bytes, encryption nonce
        :param return_bytes: bool, if True decrypted string is returned as bytes, otherwise returned as string,
            default False
        :return: Union[str, bytes], decrypted string
        """
        try:
            if isinstance(key, str):
                key = key.encode("ascii")
            if return_bytes is True:
                return AES.new(key, AES.MODE_EAX, nonce).decrypt_and_verify(message, tag)
            else:
                return AES.new(key, AES.MODE_EAX, nonce).decrypt_and_verify(message, tag).decode("utf-8", "replace")
        except ValueError as ParentException:
            raise Exceptions.SecurityError("Message integrity verification failed.") from ParentException


class Interface:
    """
    Interfacing wrapper. Contains static functions for sending and receiving messages.
    Use a Server or Client class instance to access these functions.
    """

    @staticmethod
    def send(socket_instance: Union[socket.socket, object], key: Union[bytes, None], message: Union[str, bytes]) -> \
            None:
        """
        Uses Security class to encrypt a message, sends encrypted message with provided socket object.

        :param socket_instance: Union[socket.socket, object], socket object
        :param key: Union[bytes, None], AES encryption key to be passed off to Security.encrypt, if None encryption
            does not run
        :param message: Union[str, bytes], message to be sent
        :return: None
        """
        if isinstance(message, str):
            message = message.encode("ascii", "replace")
        if key is not None:
            components = Security.encrypt(key, message)
            try:
                socket_instance.sendall(components[0] + b" |div| " + components[1] + b" |div| " + components[2])
            except socket.error as ParentException:
                raise Exceptions.InterfaceError("Failed to send message.") from ParentException
        else:
            try:
                socket_instance.sendall(message)
            except socket.error as ParentException:
                raise Exceptions.InterfaceError("Failed to send message.") from ParentException

    @staticmethod
    def receive(socket_instance: Union[socket.socket, object], key: Union[bytes, None], buffer_size: int = 4096,
                return_bytes: bool = False) -> Union[str, bytes]:
        """
        If key provided, uses Security class to decrypt a received message, returns message.
        If decrypting and message components (encrypted bytes, nonce, tag) are out of index, returns raw message.

        Return type is configurable to be bytes or string, default is string.

        :param socket_instance: Union[socket.socket, object], socket object
        :param key: Union[bytes, None], AES encryption key to be passed off to Security.decrypt, if None decryption
            does not run
        :param buffer_size: int, size of receiving buffer, default 4096
        :param return_bytes: bool, if True message is returned as bytes, otherwise returned as string, default False
        :return: Union[str, bytes], decrypted message received
        """
        try:
            byte_dump = socket_instance.recv(buffer_size)
        except socket.error as ParentException:
            raise Exceptions.InterfaceError("Failed to receive message.") from ParentException
        # i have no idea how the scope referencing
        # works out, but it workie so no need for fixie
        SWITCH = {True: byte_dump, False: byte_dump.decode("utf-8",
                                                           "replace")}
        if key is not None:
            try:
                components = byte_dump.split(b" |div| ")
            except BaseException as ParentException:
                raise Exceptions.InterfaceError("Failed to receive message.") from ParentException
            try:
                return Security.decrypt(key, components[0], components[1], components[2], return_bytes)
            except IndexError:
                return SWITCH[return_bytes]
        else:
            return SWITCH[return_bytes]


class Instance:
    """
    Plain socket wrapper factory with basic functions and class variables, however no specialization, derived for Host,
    Server, and Client. Can be utilized by the end-user for creating more derived socket classes.
    """

    def __init__(self, host: str, port: int, key: Union[str, bytes, None], key_is_path: bool = False):
        """
        Creates class socket object with supplied host and port for binding.

        :param host: str, hostname for binding or connecting
        :param port: int, port for binding or connecting
        :param key: see Security.get_key for parameter documentation, if None disables AES encryption and decryption
        :param key_is_path: see Security.get_key for parameter documentation
        :ivar self.socket: object, instance's un-abstracted socket object
        :ivar self.key: Union[bytes, None], AES encryption key or None if AES is to be disabled
        :ivar self.host: str, hostname to connect to or listen on
        :ivar self.port: int, port to connect to or listen on
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Instance.set_timeout(self, 5)
        Instance.set_blocking(self, True)
        self.key = Security.get_key(key, key_is_path)
        self.host = host
        self.port = port

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

    def send(self, message: Union[str, bytes], socket_instance: object = "DEFAULT", no_encrypt: bool = False) -> None:
        """
        See Interface.send for documentation. socket_instance is automatically set to class socket object.

        :param message: see Interface.send for parameter documentation
        :param socket_instance: see Interface.send for parameter documentation
        :param no_encrypt: bool, if True does not encrypt message, default False
        :return: None
        """
        if socket_instance == "DEFAULT":
            socket_instance = self.socket
        if no_encrypt is not False:
            key = None
        else:
            key = self.key
        Interface.send(socket_instance, key, message)

    def receive(self, buffer_size: int = 4096, socket_instance: object = "DEFAULT", no_decrypt: bool = False,
                return_bytes: bool = False) -> Union[str, bytes]:
        """
        See Interface.receive for documentation. socket_instance is automatically set to class socket object.

        :param buffer_size: see Interface.receive for parameter documentation
        :param socket_instance: see Interface.receive for parameter documentation
        :param no_decrypt: bool, if True does not decrypt message, default False
        :param return_bytes: bool, see Interface.receive for parameter documentation
        :return: Union[str, bytes], message received
        """
        if socket_instance == "DEFAULT":
            socket_instance = self.socket
        if no_decrypt is not False:
            key = None
        else:
            key = self.key
        return Interface.receive(socket_instance, key, buffer_size, return_bytes)

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
        try:
            Instance.close(self)
        except socket.error:
            pass
        except AttributeError:
            pass
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


class Host(Instance):
    """
    Host socket wrapper, derived from Instance. Factory method.
    The Host class is different from Server as it supports only one client, being simpler and more lightweight with no
    usage of threading.
    """

    def __init__(self, port: int, key: Union[str, bytes, None], host: str = "localhost", key_is_path: bool = False):
        """
        Initialize instance. See documentation for Instance.
        """
        super().__init__(host, port, key, key_is_path)
        try:
            self.socket.bind((self.host, self.port))
        except socket.error:
            Instance.restart(self)
            self.socket.bind((self.host, self.port,))
        self.client_address = None

    def listen(self) -> None:
        """
        Starts listening for connections. Is blocking.

        :return: None
        """
        Instance.set_blocking(self, True)
        self.socket.listen()
        self.socket, self.client_address = self.socket.accept()

    def disconnect(self) -> None:
        """
        Calls Instance.restart, exists to support semantics.

        :return: None
        """
        Instance.restart(self)


class ServerClientManagers:
    """
    Client managers for Server socket instances.
    Intended for testing, and end-user modification, can be piped into connection_handler parameter for Server class.
    """

    @staticmethod
    def client_manager(instance, connection_socket: Union[socket.socket, object], client_id: int) -> None:
        """
        Default thread function called for every client connection.

        :param instance: class instance
        :param connection_socket: Union[socket.socket, object], socket object from connection
        :param client_id: int, client identification
        :return: None
        """
        while True:
            sleep(1)
            # noinspection PyBroadException
            try:
                connection_socket.send(b"\x00")
            except BaseException:
                del instance.clients[client_id]
                break

    @staticmethod
    def echo(instance, connection_socket: Union[socket.socket, object], client_id: int) -> None:
        """
        Sends received bytes back to client, hence, producing an ECHO.
        Has similar behavior with ServerClientManagers.client_manager in which it will close the connection instance
        alongside client disconnect.

        :param instance: class instance
        :param connection_socket: Union[socket.socket, object], socket object from connection
        :param client_id: int, client identification
        :return: None
        """
        while True:
            sleep(1)
            # noinspection PyBroadException
            try:
                Instance.send(instance, Instance.receive(instance, socket_instance=connection_socket),
                              connection_socket)
            except BaseException:
                del instance.clients[client_id]
                break

    class ClientManager:
        """
        Client manager class template. Factory method.
        For users to derive from for their own client managers.

        To use with Server class instances, use syntax as if this class were a function.
        """

        def __init__(self, instance, connection_socket: Union[socket.socket, object], client_id: int):
            """
            Takes given parameters, and stores as class variables.

            :param instance: class instance
            :param connection_socket: Union[socket.socket, object], socket object from connection
            :param client_id: int, client identification
            """
            self.instance = instance
            self.connection_socket = connection_socket
            self.client_id = client_id

        def check_client_connected(self) -> None:
            """
            Checks if client is still connected. If not, stop instance of ClientManager.
            Loops, blocking execution.

            :return: None
            """
            while True:
                sleep(1)
                # noinspection PyBroadException
                try:
                    self.connection_socket.send(b"\x00")
                except BaseException:
                    del self.instance.clients[self.client_id]
                    break


class Server(Instance):
    """
    Server socket wrapper, derived from Instance. Factory method.
    Supports multiple clients with threading, at the cost of resource footprint and complexity.
    Has no stop function, either stop program or close socket and delete instance.
    """

    def __init__(self, port: int, key: Union[str, bytes, None],
                 connection_handler: object = ServerClientManagers.client_manager, host: str = "localhost",
                 key_is_path: bool = False, no_listen_on_init: bool = False):
        """
        Initialize instance. See documentation for Instance.

        Client connections can be accessed through self.clients class object. The dictionary is organized as:
        {0:{"address":"client.address.here", "port":0, "socket":socket_connection_object,
        "thread":client_management_thread}
        ...For each connection, where the key is the value of self.clients_handled at time of connection, creating a
        sequential integer ID.

        Begins listening for client connections immediately upon initializing, unless specified in parameters.

        :param connection_handler: function, executed as a thread with every connection, see documentation for
            Server.listen for more information, default is Server.client_manager
        :param no_listen_on_init: bool, if True, listen is not started on initialization, default False
        """
        super().__init__(host, port, key, key_is_path)
        try:
            self.socket.bind((self.host, self.port))
        except socket.error:
            Instance.restart(self)
            self.socket.bind((self.host, self.port))
        self.connection_handler = connection_handler
        self.clients_handled = 0
        self.clients = {}
        self.thread_listen = None
        self.thread_listen_kill_flag = False
        if no_listen_on_init is False:
            Server.start_listen(self)

    def kill_listen(self) -> None:
        """
        Stops listening thread, self.thread_listen.
        Start thread again with Server.start_thread.

        :return: None
        """
        self.thread_listen_kill_flag = True

    def start_listen(self) -> None:
        """
        Starts listening thread, self.thread_listen.
        Called on class initialization.

        :return: None
        """
        self.thread_listen_kill_flag = False
        self.thread_listen = threading.Thread(target=Server.listen, args=(self,), daemon=True)
        self.thread_listen.start()

    # noinspection PyTypeChecker
    def listen(self) -> None:
        """
        Listens for connections. Will block permanently until stopped.
        Thread object is automatically made for this function, and initializes with class.

        For each client connection, a thread will be started for it.
        The default thread function called is Server.client_manager, which simply checks if the connection is dead by
        sending nothing, and destroys the record in self.clients if so.

        User-customized functions can specified upon initialization. They must accept the same parameters as the default
        function, instance, connection_socket, and client_id, in those positions.
        The positional requirement is due to a limitation with assigning arguments in threads.
        instance references the current Server instance, connection_socket is the current client connection socket, and
        client_id is an int for looking up the instance in self.clients.

        :return: None
        """
        while self.thread_listen_kill_flag is False:
            Instance.set_blocking(self, True)
            self.socket.listen()
            connection_socket, client_source = self.socket.accept()
            self.clients.update({self.clients_handled: {"address": client_source[0], "port": client_source[1],
                                                        "socket": connection_socket,
                                                        "thread": threading.Thread(target=self.connection_handler,
                                                                                   args=(self, connection_socket,
                                                                                         self.clients_handled,))}})
            # thread creation above raises type warning?
            self.clients[self.clients_handled]["thread"].start()
            self.clients_handled += 1


class Client(Instance):
    """
    Client socket wrapper, derived from Instance. Factory method.
    """

    def __init__(self, host: str, port: int, key: Union[str, bytes, None], key_is_path: bool = False):
        """
        Initialize instance. See documentation for Instance.

        :param host: str, hostname of host to connect to
        :param port: int, port that host is listening on
        :param key: see Instance documentation
        :param key_is_path: see Instance documentation
        """
        super().__init__(host, port, key, key_is_path)

    def connect(self) -> None:
        """
        Starts listening for connections.

        :return: None
        """
        Instance.set_blocking(self, True)
        self.socket.connect((self.host, self.port))

    def disconnect(self) -> None:
        """
        Calls Instance.restart, exists to support semantics.

        :return: None
        """
        Instance.restart(self)
