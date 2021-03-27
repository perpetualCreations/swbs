# Another example, with AES disabled
import swbs

client = swbs.Client("127.0.0.1", 42069, b"SilentDayWeDream")
client.connect()
client.send(b"Hello world.", no_encrypt=True)
print(client.receive())
client.disconnect()