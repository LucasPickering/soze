import os
import pty
import serial


def main():
    # Init port device
    master, slave = pty.openpty()
    s_name = os.ttyname(slave)
    print("Using serial port {}".format(s_name))

    # Create serial port
    ser = serial.Serial(s_name)

    # To read from the device
    print(os.read(master, 1000).decode())

if __name__ == '__main__':
    main()
