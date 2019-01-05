import serial

from .resource import Resource
from . import logger


def format_bytes(data):
    return " ".join("{:02x}".format(b) for b in data)


class Lcd(Resource):
    def __init__(self, serial_port, *args, **kwargs):
        super().__init__(*args, sub_channel="r2d:lcd", **kwargs)
        # By deferring the port assignment until after construction, we prevent
        # the port from opening immediately, so that it can be opened manually
        self._ser = serial.Serial(
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )
        self._ser.port = serial_port

    def init(self):
        self._ser.open()

    def cleanup(self):
        self._ser.close()

    def _process_data(self, data):
        self._ser.flush()  # Make sure the buffer is empty before writing to it
        num_written = self._ser.write(data)

        # Make sure we wrote the expected number of bytes
        if num_written != len(data):
            logger.error(
                f"Expected to send {len(data)} bytes ({format_bytes(data)}),"
                f" but only sent {num_written} bytes"
            )
