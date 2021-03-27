# Example from before, with AES disabled
import swbs

client = swbs.Client("127.0.0.1", 42069, None)
client.connect()
client.send(b"Hello world.")
print(client.receive())
client.disconnect()