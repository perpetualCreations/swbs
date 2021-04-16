# Another previous example
import swbs

host = swbs.Host(42069, b"SilentDayWeDream")
host.listen()
print(host.receive(no_decrypt=True))
host.send("Something silly.")
host.disconnect()
