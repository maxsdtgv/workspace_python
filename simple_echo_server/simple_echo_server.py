import socket

try:
    address = "172.17.57.185"
    port = 1116

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = (address, port)
    sock.bind(server_address)
    prn = "Starting up on %s port %d" % (address, port)
    print(prn)
    # Listen for incoming connections
    sock.listen(1)
    # sock.connect((address, port))
    while True:
        # Wait for a connection
        connection, client_address = sock.accept()
        print('Incoming connection from %s to port %d' % (client_address[0], client_address[1]))
        while True:
            data = connection.recv(4096)
            if not data:
                print("Connection close.")
                break
            if data:
                datalen = len(data)
                prn = "Received %d of data >>" % datalen
                print(prn, data)
                print("Send back previous string ...")
                connection.sendall(data)

finally:
    sock.close()
