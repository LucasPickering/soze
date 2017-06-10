#!/usr/bin/python3

import argparse
import lcd
import socket


class SocketHandler:

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((server_ip, server_port))

    def receive(self):
        data, addr = self.sock.receive(1024)  # 1024 byte buffer
        return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('server', help="Server to receive signals from")
    parser.add_argument('port', help="Port to receive signals on", type=int)
    args = parser.parse_args()

    socket_handler = SocketHandler(args.server, args.port)

    while True:
        socket_handler.receive()


if __name__ == '__main__':
    main()
