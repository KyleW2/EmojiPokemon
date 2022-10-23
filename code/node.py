import socket

def server():
    pass

def client():
    pass

if __name__ == "__main__":
    # Get name
    name = socket.gethostname()

    # Call correct function depending on name
    if name == "server":
        server()
    else:
        client(name)