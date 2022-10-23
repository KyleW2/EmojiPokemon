import socket
import server
import client

if __name__ == "__main__":
    # Get name
    name = socket.gethostname()

    # Call correct function depending on name
    if name == "server":
        server.start()
    else:
        client.start(name)