# case-control
Software suite to control the LEDs and LCD in my computer case.
The controller is a Raspberry Pi Zero W inside my PC, powered by a USB-header to Micro-USB cable
from the motherboard to the Pi. This is also usable as an ethernet connection, but the Pi is mainly
network-connected via WiFi.


## Software
### Display (Python)
Handles interaction with the hardware. Communicates with the server via Unix Domain Sockets. This
is stateless, and merely forwards the LED/LCD settings received over the socket to the hardware.

There is also a mock display which, instead of communicating with hardware, displays the LED colors
and LCD in the console via a curses UI. This is useful for working on the client or server without
having the hardware available for testing.

Must be run on the same machine as the server.

### Server (Python)
Handles processing of user requests, and computes which values should be sent to the display.
Communicates with the client via an HTTP API (built with Flask) and the display via Unix Domain
Sockets. This holds the state for the entire program.

Must be run on the same machine as the display.

### Client (Python)
A lightweight Python abstraction for making HTTP calls to the server. This is where the user changes
settings for the system. Maintains minor state, via a config file, to make usage more convenient.
For example, you can set the server's hostname/IP and have it save in the config file, so that you
don't have to specify it for each command.

This can be run from any machine that has network access to the server.


## Installation
### Common (Display/Server)
```
sudo pip3 install -e core
```

### Display
Only on RPi - no point in doing this on any other machine
1. Follow [these steps](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c) to set up I2C on the RPi.
1. Do this:
```
sudo pip3 install -e Adafruit-Motor-HAT-Python-Library
sudo pip3 install -e py_display
sudo ln -s /path/to/case-control/py_display/ccd.service /etc/systemd/system
sudo systemctl enable ccd
```

### Server
```
sudo pip3 install -e server
sudo ln -s /path/to/case-control/server/ccs.service /etc/systemd/system
sudo systemctl enable ccs
```

### Client
```
sudo pip3 install -e client
```


## Hardware
* [Raspberry Pi Zero W](https://www.raspberrypi.org/products/pi-zero/)
* [Adafruit RGB Backlight 20x4 Character LCD](https://www.adafruit.com/product/498)
* [Adafruit LCD Backpack](https://www.adafruit.com/product/781)
* [RGB LED Strip](https://www.adafruit.com/product/346)
* [Adafruit DC & Stepper Motor HAT](https://www.adafruit.com/product/2348)


## Connections
### Power/Network
The PC is connected to the RPi via a USB cable, which goes from the motherboard's internal
5-pin USB header to the Pi's USB data port. This provides power, and has the capability of
providing a network connection as well. However the RPi is normally connected to WiFi and is
communicated with via that interface.

### LED
The RPi is connected directly to the motor HAT, and communicates with it via I2C. The HAT has four
PWM channels, but we only use three. The HAT also gets 12V/GND directly from the PSU. There is a
4-pin connection from the HAT to the LED strip, which carries 12V then a separate ground for each
color. The PWM modulates each independent GND between 0V (on) and 12V (off).

### LCD
The RPi is connected to the LCD backpack with a 3-pin connector that carries 5V, GND, and TX.
The RPi sends commands and data to the backpack with a serial connection. The serial settings are:
* 9600 baud rate
* 8 bits
* 1 stop bit
* No parity

Note that the backpack is meant to take 5V input on the data line, but the RPi only puts out 3.3V
on its GPIO pins. Fortunately, 3.3V is high enough for the backpack to recognize as logical high,
so no level converter is needed.

### PSU Keepalive
A voltage divider is used to feed the PSU's 12V output to the Raspberry Pi at ~3V. This is used to
detect when the PSU is turned off so that the LCD can be shut off too. This is necessary because
the RPi is powered by USB power, which stays on when the PSU is off.

## Pin Layout
### Raspberry Pi
Specified pin numbers use the hardware pin numbering system.

Purpose        |Pin #
---------------|---
Motor HAT 3.3V |1
Motor HAT I2C  |3,5
LCD 5V         |4
LCD GND        |6
LCD TX         |8
PSU Power In   |7

### Motor HAT
Each motor controller has two pins: `x` and `x'`, which are the two ouputs of the H-bridge.

Purpose |Pin #
--------|-----
Red     |3
Green   |1
Blue    |2'
