import itertools
import serial

from .resource import SubscriberResource
from . import logger


def chunks(l, n):
    """
    Split the given list into chunks of size n.
    https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    """
    n = max(1, n)
    return (l[i : i + n] for i in range(0, len(l), n))


def format_bytes(data):
    return " ".join("{:02x}".format(b) for b in data)


class Lcd(SubscriberResource):

    _COMMAND_QUEUE_KEY = "reducer:lcd_commands"
    # Data is sent in chunks to prevent overflowing the backpack's buffer
    _CHUNK_SIZE = 20  # Bytes per chunk

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

    def _read_data(self):
        p = self._redis.pipeline()
        p.lrange(__class__._COMMAND_QUEUE_KEY, 0, -1)
        p.delete(__class__._COMMAND_QUEUE_KEY)
        data, _ = p.execute()
        # Data is an array of bytes, convert that into one long list of ints
        return list(itertools.chain.from_iterable(data))

    def _write_data(self, data):
        # Make sure the buffer is empty before writing to it
        self._ser.flush()
        num_written = self._ser.write(data)

        # Make sure we wrote the expected number of bytes
        if num_written != len(data):
            logger.error(
                f"Expected to send {len(data)} bytes ({format_bytes(data)}),"
                f" but only sent {num_written} bytes"
            )

    def _on_pub(self, msg):
        # list of ints representing the data to transfer
        data_list = self._read_data()

        # Break the data into chunks to prevent overflowing the buffer
        data_chunks = chunks(data_list, __class__._CHUNK_SIZE)

        # Write each individual chunk
        for chunk in data_chunks:
            self._write_data(chunk)
