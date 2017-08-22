# Case-Control-CLI
CLI to control the LEDs and LCD in my computer case. Interfaces with a Raspberry Pi Zero over an
Ethernet connection, which is established via USB. The PC's program is in Java, and the Pi's is
in Python. They communicate over a socket.

## Hardware
* [Raspberry Pi Zero](https://www.raspberrypi.org/products/pi-zero/)
* [Adafruit RGB Backlight 20x4 Character LCD](https://www.adafruit.com/product/498)
* [Adafruit LCD Backpack](https://www.adafruit.com/product/781)
* [RGB LED Strip](https://www.adafruit.com/product/346)

## Connections
The PC is connected to the RPi via a USB cable, which goes from the motherboard's internal
5-pin USB header to the Pi's USB data port. This provides both power and data.

The RPi is connected to the LCD backpack with a 3-pin connector that carries 5V, GND, and TX.
The RPi sends commands and data to the backpack with a serial connection. The serial settings are:
* 9600 baud rate
* 8 bits
* 1 stop bit
* No parity

Note that the backpack is meant to take 5V input on the data line, but the RPi only puts out 3.3V
on its GPIO pins. Fortunately, 3.3V is high enough for the backpack to recognize as logical high,
so no level converter is needed.

The RPi is connected to the LEDs via a small board I made, which contains 3 MOSFETs. Each MOSFET
corresponds to one color in RGB. The gate of each MOSFET is connected to its respective GPIO pin
on the RPi. Each source is connected to its respective color on the LED strip, and each drain is
connected to GND from the PSU. The LED strip has one common cathode, which is powered with 12V from
the PSU.


## Raspberry Pi Pin Layout
Specified pin numbers use the hardware pin numbering system.

Purpose|Pin #
---|---
LED Red|5
LED Green|3
LED Blue|7
LCD 5V|4
LCD GND|6
LCD TX|8
