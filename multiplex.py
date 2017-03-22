#!/usr/bin/env python3

import argparse
import socket
import select

# some "evil" globals
sockets = [];
serverSocket = None

def connectToServer():
    global serverSocket, sockets, serverName, serverPort

    try:
        serverSocket = socket.create_connection((serverName, serverPort));
        sockets.append(serverSocket)
    except:
        serverSocket = None

def closeServerConnection():
    global serverSocket, sockets

    sockets.remove(serverSocket)
    serverSocket.close()
    serverSocket = None

parser = argparse.ArgumentParser(description='Forward traffic from server to multiple clients');
parser.add_argument('remote')
parser.add_argument('local')
parser.add_argument('--nodelay', action="store_true")

args = parser.parse_args()

serverName, ignore, serverPort = args.remote.partition(':')
address, sep, port = args.local.partition(':')

if sep == '':
    port = address
    address = '*'
elif address == '':
    address = '*'

# create sockets
localAddrs = socket.getaddrinfo(address, port, proto=socket.IPPROTO_TCP)
listeningSockets = [];
for (family, sockType, protocol, ignore, sockAddr) in localAddrs:
    s = socket.socket(family, sockType, protocol)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(sockAddr)
    s.listen(10)
    listeningSockets.append(s)

sockets.extend(listeningSockets)
clients = []

while True:
    if serverSocket == None:
        connectToServer()

    readSocks, writeSocks, errSocks = select.select(sockets, [], sockets, 5)
    for s in readSocks:
        if s == serverSocket and serverSocket != None:
            # got data from the remote server read and multiplex to clients
            buf = s.recv(1024)
            if len(buf) > 0:
                for client in clients:
                    client.sendall(buf)
            else:
                closeServerConnection()
        elif s in listeningSockets:
            # a new client connects
            client, addr = s.accept()
            clients.append(client)
            sockets.append(client)
            if args.nodelay:
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        elif s in clients:
            # connection from clients are read-only, so drain the buffer only
            # or the connection is reset/eof
            buf = s.recv(1024)
            if len(buf) == 0:
                errSocks.append(s)

    # handle faulted client connections
    for s in errSocks:
        if s in clients:
            sockets.remove(s)
            clients.remove(s)
            s.close();

    if serverSocket in errSocks:
        closeServerConnection()
