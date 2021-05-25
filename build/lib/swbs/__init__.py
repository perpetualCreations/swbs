"""
Socket Wrapper for Byte Strings (SWBS).

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


class Exceptions:
    """Parent class for child classes serving as exceptions deriving from \
        BaseException."""

    class SecurityError(BaseException):
        """Exception raised by Security class."""

    class InterfaceError(BaseException):
        """Exception raised by Interface class."""

    class ServerError(BaseException):
        """Exception raised by Server class instance."""

    class ClientError(BaseException):
        """Exception raised by Client class instance."""


class Security:
    """AES security wrapper. Contains security-related static functions."""

    @staticmethod
    def generate_key(dump_to_path: Union[str, None] = None,
                     random_max: int = 1024,
                     random_min: int = 16) -> Union[bytes, None]:
        """
        Generate a random 16-byte AES key bytestring, by creating a random \
            string of characters, length between random_max and random_min, \
            and hashing the string. Generated key can be returned or \
            written to a file.

        :param dump_to_path: if provided string, parameter is interpreted as
            path to a file for key to be written to, otherwise key is
            returned, default None
        :type dump_to_path: Union[str, None]
        :param random_max: maximum random character length for key
            generation through hashing, default 1024
        :type random_max: int
        :param random_min: int, minimum random character length for key
            generation through hashing, default 16
        :type random_min: int
        :return: if dump_to_path is not string, return bytes being the key,
            otherwise return None
        :rtype: Union[bytes, None]
        """
        random_min = min(max(random_min, 1), random_max)
        if isinstance(dump_to_path, str) is True:
            with open(dump_to_path, "wb") as key_dump:
                key_dump.write(MD5.new(urandom(randint(random_min, random_max))
                                       ).hexdigest().encode("ascii"))
        else:
            return MD5.new(urandom(randint(random_min, random_max))
                           ).hexdigest().encode("ascii")

    @staticmethod
    def get_key(key: Union[str, bytes, None],
                key_is_path: bool = False) -> Union[bytes, None]:
        """
        Collect key, if already bytes and not from path, returns bytes again.

        :param key: if key_is_path is False,
            key string, otherwise path to key file, if None return None
        :type key: Union[str, bytes, None]
        :param key_is_path: if True, key parameter is treated as path to
            key file for reading from, default False
        :type key_is_path: bool
        :return: encryption key
        :rtype: bytes
        """
        if key is None:
            return None
        if key_is_path is True:
            try:
                with open(key, "rb") as key_handle:
                    key = key_handle.read()
            except FileNotFoundError as ParentException:
                raise Exceptions.SecurityError("Key file does not exist.") \
                    from ParentException
        if isinstance(key, str):
            key = key.encode("ascii", "replace")
        if len(key) != 16:
            raise Exceptions.SecurityError("Key length is not 16, cannot be "
                                           "used for AES encryption.")
        return key

    @staticmethod
    def encrypt(key: Union[str, bytes], message: Union[str, bytes]) -> list:
        """
        Encrypts a string with a 16-byte key for AES, returns encrypted \
            contents.

        :param key: AES encryption key
        :type key: Union[str, bytes]
        :param message: message for encryption
        :type message: Union[str, bytes]
        :return: encrypted message, tag, nonce
        :rtype: list
        """
        if isinstance(message, str):
            message = message.encode("ascii", "replace")
        if isinstance(key, str):
            key = key.encode("ascii")
        encryptor = AES.new(key, AES.MODE_EAX)
        encrypted, tag = encryptor.encrypt_and_digest(message)
        return [encrypted, tag, encryptor.nonce]

    @staticmethod
    def decrypt(key: Union[str, bytes], message: bytes, tag: bytes,
                nonce: bytes, return_bytes: bool = False) -> Union[str, bytes]:
        """
        Decrypts a string with a 16-byte key for AES, tag, and nonce, returns \
            decrypted string or bytes, default string.

        :param key: AES encryption key
        :type key: Union[str, bytes]
        :param message: message for decryption
        :type message: bytes
        :param tag: encryption tag
        :type tag: bytes
        :param nonce: encryption nonce
        :type nonce: bytes
        :param return_bytes: if True decrypted string is returned as bytes,
            otherwise returned as string, default False
        :type return_bytes: bool
        :return: decrypted string
        :rtype: Union[str, bytes]
        """
        try:
            if isinstance(key, str):
                key = key.encode("ascii")
            if return_bytes is True:
                return AES.new(key, AES.MODE_EAX, nonce
                               ).decrypt_and_verify(message, tag)
            else:
                return AES.new(key, AES.MODE_EAX, nonce
                               ).decrypt_and_verify(
                                   message, tag).decode("utf-8", "replace")
        except ValueError as ParentException:
            raise Exceptions.SecurityError(
                "Message integrity verification failed.") from ParentException


class Interface:
    """
    Interfacing wrapper.

    Contains static functions for sending and receiving messages.
    Use a Server or Client class instance to access these functions.
    """

    @staticmethod
    def send(socket_instance: Union[socket.socket, object],
             key: Union[bytes, None], message: Union[str, bytes]) -> None:
        """
        Use Security class to encrypt a message, sends encrypted message \
            with provided socket object.

        :param socket_instance: socket object
        :type socket_instance: Union[socket.socket, object]
        :param key: AES encryption key to be passed off to Security.encrypt,
            if None encryption does not run
        :type key: Union[bytes, None]
        :param message: message to be sent
        :type message: Union[str, bytes]
        """
        if isinstance(message, str):
            message = message.encode("ascii", "replace")
        if key is not None:
            components = Security.encrypt(key, message)
            try:
                socket_instance.sendall(components[0] + b" |div| " +
                                        components[1] + b" |div| " +
                                        components[2])
            except socket.error as ParentException:
                raise Exceptions.InterfaceError("Failed to send message.") \
                    from ParentException
        else:
            try:
                socket_instance.sendall(message)
            except socket.error as ParentException:
                raise Exceptions.InterfaceError("Failed to send message.") \
                    from ParentException

    @staticmethod
    def receive(socket_instance: Union[socket.socket, object],
                key: Union[bytes, None], buffer_size: int = 4096,
                return_bytes: bool = False) -> Union[str, bytes]:
        """
        If key provided, uses Security class to decrypt a received message, \
            returns message.

        If decrypting and message components (encrypted bytes, nonce, tag) are
        out of index, returns raw message.
        Return type is configurable to be bytes or string, default is string.

        :param socket_instance: socket object
        :type socket_instance: Union[socket.socket, object]
        :param key: AES encryption key to be passed off to Security.decrypt,
            if None decryption does not run
        :type key: Union[bytes, None]
        :param buffer_size: size of receiving buffer, default 4096
        :type buffer_size: int
        :param return_bytes: if True message is returned as bytes, otherwise
            returned as string, default False
        :type return_bytes: bool
        :return: decrypted message received
        :rtype: Union[str, bytes]
        """
        try:
            byte_dump = socket_instance.recv(buffer_size)
        except socket.error as ParentException:
            raise Exceptions.InterfaceError("Failed to receive message.") \
                from ParentException
        # i have no idea how the scope referencing
        # works out, but it workie so no need for fixie
        SWITCH = {True: byte_dump, False: byte_dump.decode("utf-8",
                                                           "replace")}
        if key is not None:
            try:
                components = byte_dump.split(b" |div| ")
            except BaseException as ParentException:
                raise Exceptions.InterfaceError("Failed to receive message.") \
                    from ParentException
            try:
                return Security.decrypt(key, components[0], components[1],
                                        components[2], return_bytes)
            except IndexError:
                return SWITCH[return_bytes]
        else:
            return SWITCH[return_bytes]


class Instance:
    """
    Plain socket wrapper factory.

    Has basic functions and class variables, however no specialization,
    derived for Host, Server, and Client. Can be utilized by the end-user for
    creating more derived socket classes.
    """

    def __init__(self, host: str, port: int, key: Union[str, bytes, None],
                 key_is_path: bool = False):
        """
        Create class socket object with supplied host and port for binding.

        :param host: hostname for binding or connecting
        :type host: str
        :param port: port for binding or connecting
        :type port: int
        :param key: see Security.get_key for parameter documentation, if None
            disables AES encryption and decryption
        :param key_is_path: see Security.get_key for parameter documentation
        :ivar self.socket: object, instance's un-abstracted socket object
        :ivar self.key: Union[bytes, None], AES encryption key or None if AES
            is to be disabled
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

        :param state: whether socket should be blocking
        :type state: bool
        """
        self.socket.setblocking(state)

    def set_timeout(self, time: int) -> None:
        """
        Set instance's socket's seconds until timeout.

        :param time: seconds until timeout
        :type time: int
        """
        self.socket.settimeout(time)

    def send(self, message: Union[str, bytes],
             socket_instance: object = "DEFAULT",
             no_encrypt: bool = False) -> None:
        """
        See Interface.send for documentation. socket_instance is \
            automatically set to class socket object.

        :param message: see Interface.send for parameter documentation
        :param socket_instance: see Interface.send for parameter documentation
        :param no_encrypt: if True does not encrypt message, default False
        :type no_encrypt: bool
        """
        if socket_instance == "DEFAULT":
            socket_instance = self.socket
        if no_encrypt is not False:
            key = None
        else:
            key = self.key
        Interface.send(socket_instance, key, message)

    def receive(self, buffer_size: int = 4096,
                socket_instance: object = "DEFAULT", no_decrypt: bool = False,
                return_bytes: bool = False) -> Union[str, bytes]:
        """
        See Interface.receive for documentation. socket_instance is \
            automatically set to class socket object.

        :param buffer_size: see Interface.receive for parameter
            documentation
        :param socket_instance: see Interface.receive for parameter
            documentation
        :param no_decrypt: if True does not decrypt message, default False
        :type no_decrypt: bool
        :param return_bytes: see Interface.receive for parameter documentation
        :type return_bytes: bool
        :return: message received
        :rtype: Union[str, bytes]
        """
        if socket_instance == "DEFAULT":
            socket_instance = self.socket
        if no_decrypt is not False:
            key = None
        else:
            key = self.key
        return Interface.receive(socket_instance, key, buffer_size,
                                 return_bytes)

    def close(self) -> None:
        """Close Instance socket. If applicable, effectively closes \
            connections."""
        self.socket.close()

    def restart(self) -> None:
        """Close and reopen Instance socket. If applicable, effectively \
            closes connections, like Instance.close."""
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

    The Host class is different from Server as it supports only one client,
    being simpler and more lightweight with no usage of threading.
    """

    def __init__(self, port: int, key: Union[str, bytes, None],
                 host: str = "localhost", key_is_path: bool = False):
        """Initialize instance. See documentation for Instance."""
        super().__init__(host, port, key, key_is_path)
        try:
            self.socket.bind((self.host, self.port))
        except socket.error:
            Instance.restart(self)
            self.socket.bind((self.host, self.port,))
        self.client_address = None

    def listen(self) -> None:
        """Start listening for connections. Is blocking."""
        Instance.set_blocking(self, True)
        self.socket.listen()
        self.socket, self.client_address = self.socket.accept()

    def disconnect(self) -> None:
        """Call Instance.restart, exists to support semantics."""
        Instance.restart(self)


class ServerClientManagers:
    """
    Client managers for Server socket instances.

    Intended for testing, and end-user modification, can be piped into
    connection_handler parameter for Server class.
    """

    @staticmethod
    def client_manager(instance,
                       connection_socket: Union[socket.socket, object],
                       client_id: int) -> None:
        """
        Thread function called for every client connection.

        :param instance: class instance
        :param connection_socket: socket object from connection
        :type connection_socket: Union[socket.socket, object]
        :param client_id: client identification
        :type client_id: int
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
    def echo(instance, connection_socket: Union[socket.socket, object],
             client_id: int) -> None:
        """
        Send received bytes back to client, hence, producing an ECHO.

        Has similar behavior with ServerClientManagers.client_manager in
        which it will close the connection instance alongside client
        disconnect.

        :param instance: class instance
        :param connection_socket: socket object from connection
        :type connection_socket: Union[socket.socket, object]
        :param client_id: client identification
        :type client_id: int
        :return: None
        """
        while True:
            sleep(1)
            # noinspection PyBroadException
            try:
                Instance.send(instance,
                              Instance.receive(
                                  instance, socket_instance=connection_socket),
                              connection_socket)
            except BaseException:
                del instance.clients[client_id]
                break

    class ClientManager:
        """
        Client manager base class template. Factory method.

        For users to derive from for their own client managers.
        """

        def __init__(self, instance,
                     connection_socket: Union[socket.socket, object],
                     client_id: int):
            """
            Take given parameters, and stores as class variables.

            :param instance: class instance
            :param connection_socket: socket object from connection
            :type connection_socket: Union[socket.socket, object]
            :param client_id: client identification
            :type client_id: int
            :ivar self.instance: dump of parameter instance
            :ivar self.connection_socket: dump of parameter connection_socket
            :ivar self.client_id: dump of parameter client_id
            """
            self.__bases__ = ()
            self.instance = instance
            self.connection_socket = connection_socket
            self.client_id = client_id

        def check_client_connected(self) -> None:
            """
            Check if client is still connected. If not, \
                stop instance of ClientManager.

            Loops, blocking execution.
            """
            while True:
                sleep(1)
                # noinspection PyBroadException
                try:
                    self.connection_socket.send(b"\x00")
                except BaseException:
                    del self.instance.clients[self.client_id]
                    break

    class ClientManagerInstanceExposed(ClientManager, threading.Thread):
        """
        The same as ServerClientManagers.ClientManager, base class.

        However, the ClientManager thread is exposed when executed by
        Server.listen, the object returned by the "thread" key is the class
        instance. This allows code outside of the thread to access instance
        variables and functions.

        However, any code to be ran whilst as a thread needs to be declared in
        a function called "run" with no parameters supported (except self,
        not to be static). Use __init__ for initialization only, and write
        actual execution in the aforementioned .run() function.

        This is achieved through using threading.Thread as a base.
        In result, expect inherited functions and attributes.
        """

        def __init__(self, instance,
                     connection_socket: Union[socket.socket, object],
                     client_id: int):
            """
            Take given parameters, and stores as class variables.

            :param instance: class instance
            :param connection_socket: socket object from connection
            :type connection_socket: Union[socket.socket, object]
            :param client_id: client identification
            :type client_id: int
            :ivar self.instance: dump of parameter instance
            :ivar self.connection_socket: dump of parameter connection_socket
            :ivar self.client_id: dump of parameter client_id
            """
            super().__init__(instance=instance,
                             connection_socket=connection_socket,
                             client_id=client_id)
            threading.Thread.__init__(self)


class Server(Instance):
    """
    Server socket wrapper, derived from Instance. Factory method.

    Supports multiple clients with threading, at the cost of resource
    footprint and complexity. Has no stop function, either stop program or
    close socket and delete instance.
    """

    def __init__(self, port: int, key: Union[str, bytes, None],
                 connection_handler:
                     callable = ServerClientManagers.client_manager,
                 host: str = "localhost",
                 key_is_path: bool = False, no_listen_on_init: bool = False):
        """
        Initialize instance. See documentation for Instance.

        Client connections can be accessed through self.clients class object.
        The dictionary is organized as:
        {0:{"address":"client.address.here", "port":0,
        "socket":socket_connection_object, "thread":client_management_thread}
        ...For each connection, where the key is the value of
        self.clients_handled at time of connection, creating a sequential
        integer ID.

        Begins listening for client connections immediately upon initializing,
        unless specified in parameters.

        :param connection_handler: executed as a thread with every connection,
            see documentation for Server.listen for more information,
            default is Server.client_manager, to specify this parameter
            enter the name of the class or function with no parentheses after
        :type connection_handler: callable
        :param no_listen_on_init: if True, listen is not started on
            initialization, default False
        :type no_listen_on_init: bool
        """
        super().__init__(host, port, key, key_is_path)
        try:
            self.socket.bind((self.host, self.port))
        except socket.error:
            Instance.restart(self)
            self.socket.bind((self.host, self.port))
        self.connection_handler: callable = connection_handler
        self.clients_handled = 0
        self.clients = {}
        self.thread_listen = None
        self.thread_listen_kill_flag = False
        if no_listen_on_init is False:
            Server.start_listen(self)

    def kill_listen(self) -> None:
        """
        Stop listening thread, self.thread_listen.

        Start thread again with Server.start_thread.
        """
        self.thread_listen_kill_flag = True

    def start_listen(self) -> None:
        """
        Start listening thread, self.thread_listen.

        Called on class initialization.
        """
        self.thread_listen_kill_flag = False
        self.thread_listen = threading.Thread(target=Server.listen,
                                              args=(self,), daemon=True)
        self.thread_listen.start()

    # noinspection PyTypeChecker
    def listen(self) -> None:
        """
        Listen for connections. Will block permanently until stopped.

        Thread object is automatically made for this function, and initializes
        with class.

        For each client connection, a thread will be started for it.
        The default thread function called is Server.client_manager,
        which simply checks if the connection is dead by
        sending nothing, and destroys the record in self.clients if so.

        User-customized functions can specified upon initialization.
        They must accept the same parameters as the default function,
        instance, connection_socket, and client_id, in those positions.
        The positional requirement is due to a limitation with assigning
        arguments in threads.
        instance references the current Server instance, connection_socket is
        the current client connection socket, and
        client_id is an int for looking up the instance in self.clients.
        """
        while self.thread_listen_kill_flag is False:
            Instance.set_blocking(self, True)
            self.socket.listen()
            connection_socket, client_source = self.socket.accept()
            try:
                if ServerClientManagers.ClientManagerInstanceExposed in \
                        self.connection_handler.__bases__:
                    # warning can be safely ignored
                    thread = self.connection_handler(
                        self, connection_socket, self.clients_handled)
                else:
                    thread = threading.Thread(
                        target=self.connection_handler,
                        args=(self, connection_socket,
                              self.clients_handled,))
            except AttributeError:
                thread = threading.Thread(
                    target=self.connection_handler,
                    args=(self, connection_socket,
                          self.clients_handled,))
            self.clients.update(
                {self.clients_handled: {"address": client_source[0],
                                        "port": client_source[1],
                                        "socket": connection_socket,
                                        "thread": thread}})
            self.clients[self.clients_handled]["thread"].start()
            self.clients_handled += 1


class Client(Instance):
    """Client socket wrapper, derived from Instance. Factory method."""

    def __init__(self, host: str, port: int, key: Union[str, bytes, None],
                 key_is_path: bool = False):
        """
        Initialize instance. See documentation for Instance.

        :param host: hostname of host to connect to
        :type host: str
        :param port: port that host is listening on
        :type port: int
        :param key: see Instance documentation
        :param key_is_path: see Instance documentation
        """
        super().__init__(host, port, key, key_is_path)

    def connect(self) -> None:
        """Start listening for connections."""
        Instance.set_blocking(self, True)
        self.socket.connect((self.host, self.port))

    def disconnect(self) -> None:
        """Call Instance.restart, exists to support semantics."""
        Instance.restart(self)
