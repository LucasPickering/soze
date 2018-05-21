import serial

from . import logger
from .resource import Resource, format_bytes

BAUD_RATE = 9600


class Lcd(Resource):
    def __init__(self, sock_addr, serial_port):
        super().__init__('LCD', sock_addr)

        self._ser = serial.Serial(serial_port,
                                  baudrate=BAUD_RATE,
                                  bytesize=serial.EIGHTBITS,
                                  parity=serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE)

    def _process_data(self, data):
        self._ser.flush()  # Make sure the buffer is empty before writing more to it
        num_written = self._ser.write(data)

        # Make sure we wrote the expected number of bytes
        if num_written != len(data):
            logger.error(f"Expected to send {len(data)} bytes ({format_bytes(data)}),"
                         f" but only sent {num_written} bytes")

    def close(self):
        super().close()
        self._ser.close()
