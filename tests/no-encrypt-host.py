import swbs

host = swbs.Host(port=42069, key=None)
host.listen()
print(host.receive())
host.send("Something silly.")
host.disconnect()