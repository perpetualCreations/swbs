# Socket Wrapper for Byte Strings
A straight-forward wrapper for sending and receiving byte strings with sockets.

## Install
Download the Python wheel file from the Github repository release, and install manually using:
```commandline
pip3 install /path/to/wheel/file/here/swbs-1.0.whl
```
Or install through PyPI, using:
```commandline
pip3 install swbs
```

## How to Use
You'll be creating two scripts, one running the socket server, and the other the client.

The server and client can send and receive both ways, regardless of their role. 

The server must run first, to listen for the client's connection. Please plan accordingly, for you specific implementation.

#### Import
First start by importing the package.
```python
import swbs
```

#### Configure
You'll then need to configure SWBS, through `swbs.configure`.

Within `swbs.configure` are functions `security`, `role`, `destination` and `endpoint`.

`swbs.configure.security` takes four parameters. 

The first is a string, used as the encryption key. 

The second another string, used as the HMAC key. 

The third is again, another string, for authenticating hosts. Think of it like a password. 

The final parameter is optional, and accepts a True or False boolean, it only applies to the server script. 
It signals whether the authentication string is a SHA3 256 hash, and when comparing the client's given authentication string, should hash the given string and compare.

This is useful for implementations where the authentication string cannot be stored in plaintext. By default though, this is disabled.
To turn this option on, set this parameter to True.

Please ensure you have set the same keys for both the server and client scripts.

`swbs.configure.role` takes one parameter, a True or False boolean. 

If set to True, SWBS will take the role of the server. By default, the role is set to False, signaling to operate as a client.
 
 #### Client Only
 
`swbs.configure.destination` takes two parameters. It only applies to the client script.

The first is a string, being the IP address of the server. Point this to the address of the host that the server script is running on.
If you're running both of them on your computer for testing purposes, set this to `"localhost"` or `"127.0.0.1"`.

The second is an integer, being the port the server is listening to. By default, this is set to port 64220. You may change this, however the port must be the same across the client and server.

 Client example:
 
```python
import swbs
swbs.configure.security("some encryption key", "an hmac key", "auth string")
swbs.configure.role(False)
swbs.configure.destination("localhost", 2234) # localhost can be replaced with an IP such as 192.168.1.1, if your using the default port, you may forgo the second parameter# .
```

#### Server Only

`swbs.configure.endpoint` takes three parameters. It only applies to the server script.

The first is a string, being the hostname (IP) of the server. By default this is `"localhost"` or `"127.0.0.1"`.

The second is an integer, being the port the server is listening to. By default, this is set to port 64220. You may change this, however the port must be the same across the client and server.

The third is optional, and is a True/False boolean, signaling whether to automatically retrieve the hostname of the server. By default, this is set to False.

Server example:

```python
import swbs
swbs.configure.security("some encryption key", "an hmac key", "auth string")
swbs.configure.role(False)
swbs.configure.destination("localhost", 2234) # localhost can be replaced with an IP such as 192.168.1.1, if your using the default port, you may forgo the second parameter# .
```

#### Connect and Accept

After configuring, you can have the client try connecting to the server!

`swbs.interface` contains the functions for the client and server to interact. See below on how they are used.

#### Client Only

`swbs.interface.connect` as the name suggests, is a function that connects the client to the server.
It does not take any parameters, it works off what you have already configured.

Using this function, the example now looks like:

```python
import swbs
swbs.configure.security("some encryption key", "an hmac key", "auth string")
swbs.configure.role(False)
swbs.configure.destination("localhost", 2234) # localhost can be replaced with an IP such as 192.168.1.1, if your using the default port, you may forgo the second parameter# .
swbs.interface.connect()
```

#### Server Only

`swbs.interface.accept` as the name suggests, is a function that accepts connections from the client.
It does not take any parameters, it works off what you have already configured.

This function is blocking, meaning it will halt your script until a connection is made.

Using this function, the example now looks like:

```python
import swbs
swbs.configure.security("some encryption key", "an hmac key", "auth string")
swbs.configure.role(False)
swbs.configure.destination("localhost", 2234) # localhost can be replaced with an IP such as 192.168.1.1, if your using the default port, you may forgo the second parameter# .
swbs.interface.accept()
```

#### Send and Receive

After adding functions for establishing the connection, we can now use the send and receive functions.

To this, we can use functions `swbs.interface.send` and `swbs.interface.receive`.

Both functions accept one parameter, a string or bytestring, which is the message to be sent.

`swbs.interface.receive` however has a second, optional parameter, that accepts a True or False boolean, signaling whether to decode the bytestring, and instead return a regular string.

Our code examples from before, now using these functions, now look like this:

Client example:

```python
import swbs
swbs.configure.security("some encryption key", "an hmac key", "auth string")
swbs.configure.role(False)
swbs.configure.destination("localhost", 2234) # localhost can be replaced with an IP such as 192.168.1.1, if your using the default port, you may forgo the second parameter# .
swbs.interface.connect()
swbs.interface.send("hello world") # this can also be a bytestring
```

Server example:

```python
import swbs
swbs.configure.security("some encryption key", "an hmac key", "auth string")
swbs.configure.role(False)
swbs.configure.destination("localhost", 2234) # localhost can be replaced with an IP such as 192.168.1.1, if your using the default port, you may forgo the second parameter# .
swbs.interface.accept()
print(swbs.interface.receive(True)) # you can also have swbs.interface.receive pipe into a variable
```

#### Disconnect

When your script has finished sending and receiving, or your application terminated, we want to close the connection.

We can do this by using `swbs.interface` again, with the `disconnect` function. 
After disconnecting, you can always restart the connection by running `swbs.interface.connect` and `swbs.interface.accept`.

Now our code example looks like this:

Client example:

```python
import swbs
swbs.configure.security("some encryption key", "an hmac key", "auth string")
swbs.configure.role(False)
swbs.configure.destination("localhost", 2234) # localhost can be replaced with an IP such as 192.168.1.1, if your using the default port, you may forgo the second parameter# .
swbs.interface.connect()
swbs.interface.send("hello world") # this can also be a bytestring
swbs.interface.disconnect()
```

Server example:

```python
import swbs
swbs.configure.security("some encryption key", "an hmac key", "auth string")
swbs.configure.role(False)
swbs.configure.destination("localhost", 2234) # localhost can be replaced with an IP such as 192.168.1.1, if your using the default port, you may forgo the second parameter# .
swbs.interface.accept()
print(swbs.interface.receive(True)) # you can also have swbs.interface.receive pipe into a variable
swbs.interface.disconnect()
```

#### Conclusion

This concludes our walkthrough of using the SWBS package. 

If you would like to see a pre-written example, see the tests directory in the repository.

And remember, the server script must be running first, before any client can connect to it.

### Future

More features are planned, such as a `reconnect` function for the `interface` module. 
These will see implementation in future releases.

### End
This is the end of the documentation for the SWBS package.

Please visit https://dreamerslegacy.xyz for other projects, and for contact info in the case of any inquiries.

This project was built off of the `comms` module of the Raspbot project's control application. 
