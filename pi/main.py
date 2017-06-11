#!/usr/bin/python3

import argparse
import socket
import struct
import threading
from lcd import Lcd
from collections import namedtuple


CaseSettings = namedtuple('CaseSettings', 'color')
LcdSettings = namedtuple('LcdSettings', 'color text')


class SocketHandler:

    def __init__(self, server_port):
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", server_port))  # Bind the socket to the specified port

    def receive(self):
        data, addr = self.sock.recvfrom(1024)  # 1024 byte buffer
        return data

    def close(self):
        self.sock.close()


class Main:

    def __init__(self, args):
        self.run = True

        self.socket_handler = SocketHandler(args.udp)
        self.socket_thread = threading.Thread(target=self.socket_thread)

        self.lcd = Lcd(args.serial)
        self.lcd.set_autoscroll(False)
        self.lcd.on()
        self.lcd.clear()
        self.lcd_thread = threading.Thread(target=self.lcd_thread)

    def start(self):
        self.socket_thread.start()
        self.lcd_thread.start()

    def stop(self):
        self.run = False

    def __decode_packet(self, packet):
        # Decode the colors
        color_bytes = packet[:6]  # First size bytes of the packet are colors
        color_data = struct.unpack('!3B 3B', color_bytes)
        case_color = color_data[:3]  # First 3 bytes are the case color
        lcd_color = color_data[3:]  # Last 3 bytes are the LCD color

        text_bytes = packet[6:]  # Rest of the packet is text
        lcd_text = text_bytes.decode('utf-8')

        return Settings(case_color, lcd_color, lcd_text)

    def socket_thread(self):
        while self.run:
            try:
                packet = self.socket_handler.receive()
                settings = self.__decode_packet(packet)
                print(settings)
                self.lcd.set_color(*settings.lcd_color)
                self.lcd.set_text(settings.lcd_text)
            except KeyboardInterrupt:
                break
        self.socket_handler.close()

    def lcd_thread(self):



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--udp', type=int, default=5555,
                        help="UDP port to receive settings on")
    parser.add_argument('-s', '--serial', default='/dev/ttyAMA0',
                        help="Serial port to communicate with the LCD on")
    args = parser.parse_args()

    main = Main(args)
    main.start()


if __name__ == '__main__':
    main()
