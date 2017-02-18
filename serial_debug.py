import os
import pty
import serial
import sys


def read_byte(master):
    return int.from_bytes(os.read(master, 1), byteorder='big')


def main():
    # Init port device
    master, slave = pty.openpty()
    s_name = os.ttyname(slave)
    print("Using serial port {}".format(s_name))

    # Create serial port
    ser = serial.Serial(s_name)

    # Read from the device
    state = None
    while True:
        state = read_byte(master)
        if state == ord('c'):
            red = read_byte(master)
            green = read_byte(master)
            blue = read_byte(master)
            sys.stdout.write("\rRed: {}; Green: {}; Blue: {}     ".format(red, green, blue))
        else:
            pass


if __name__ == '__main__':
    main()
