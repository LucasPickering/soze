# Söze

_The greatest trick the devil ever pulled was convincing the world he did not exist._

Software suite to control the LEDs and LCD in my computer case. The controller is a Raspberry Pi Zero W inside my PC, powered by a USB-header to Micro-USB cable from the motherboard to the RPi. This is also used as an ethernet connection.

## Software

### API (Python)

HTTP API to expose configuration to the user. GETs and POSTs allow the user to fetch and update state. The user state is stored exclusively in Redis, so every HTTP request will create at least one Redis request.

### Reducer (Python)

Handles state processing. Periodically calculates derived state (the values that the hardware actually shows) from user state (the values that the user configures via the API). Pulls user state from Redis and pushes derived state to Redis.

### Display (Python)

Handles interaction with the hardware. Communicates with the reducer via Redis. This is stateless, and merely forwards the LED/LCD settings received from Redis to the hardware.

There is also a mock display which, instead of communicating with hardware, displays the LED colors and LCD in the console via a curses UI. This is useful for working on other components without having the hardware available for testing.

### Webapp (JavaScript)

A React-based webpage that exposes configuration. This is just a few pretty controls that visualize the user state. Generates HTTP requests to get and update user state. Runs from a webserver (Nginx) on the RPi, but this could run on any machine with network access to the RPi.

## Installation

### Development

There are two ways of running this in development. The typical way involves the terminal-based mock display. You can also run it with the hardware display and mock the hardware libraries. This allows you to test the code in `hw_display/`, but the hardware output is just logged to files instead of being visual. This is good for testing `hw_display/` code, but not if you're working on any other components.

#### Terminal Mock Display

In one terminal window:

```
docker-compose up
```

and in another:

```
cd mock_display
python3 -m soze_display
```

Docker Compose will run all the services (webapp, API, reducer, Redis) that you need. The mock display has to be run separately because it controls the entire

#### Hardware Display w/ Mock Libraries

```
docker-compose -f docker-compose.hw-display.yml up
```

Then the log files with the hardware output will all be in `hw_display/`.

### Production

The RPi should have a Docker server running on it. All Docker commands can be run remotely, as long as the client is properly pointed at the server, like so:

```
export DOCKER_HOST=<RPi addr/hostname>:2375  # Bash
$env:DOCKER_HOST = '<RPi addr/hostname>:2375'  # Powershell
```

Now, all Docker commands run in that shell will point to the RPi. Build the webapp with:

```
cd webapp
npm run build
cd ..
```

Then, start the services:

```
docker-compose -f docker-compose.pi.yml up -d
```

If you change code in a component, you'll have to rebuild its image, because the code is loaded into the image at build time.

```
docker-compose -f docker-compose.pi.yml build [<component>...]
```

## Hardware

- [Raspberry Pi Zero W](https://www.raspberrypi.org/products/pi-zero/)
- [Adafruit RGB Backlight 20x4 Character LCD](https://www.adafruit.com/product/498)
- [Adafruit LCD Backpack](https://www.adafruit.com/product/781)
- [RGB LED Strip](https://www.adafruit.com/product/346)
- [Adafruit DC & Stepper Motor HAT](https://www.adafruit.com/product/2348)

## Connections

### Power/Network

The PC is connected to the RPi via a USB cable, which goes from the motherboard's internal 5-pin USB header to the RPi's USB data port. This provides power, and has the capability of providing a network connection as well. The RPi can also connect to WiFi, but the connection is shoddy because it's inside a metal cage.

### LED

The RPi is connected directly to the motor HAT, and communicates with it via I2C. The HAT has four PWM channels, but we only use three. The HAT also gets 12V/GND directly from the PSU. There is a 4-pin connection from the HAT to the LED strip, which carries 12V then a separate ground for each color channel (RGB). The PWM modulates each independent GND between 0V (on) and 12V (off).

### LCD

The RPi is connected to the LCD backpack with a 3-pin connector that carries 5V, GND, and TX. The RPi sends commands and data to the backpack via UART. The UART settings are:

- 9600 baud rate
- 8 bits
- 1 stop bit
- No parity

Note that the backpack is meant to take 5V input on the data line, but the RPi only puts out 3.3V on its GPIO pins. Fortunately, 3.3V is high enough for the backpack to recognize as logical high, so no level converter is needed.

### PSU Keepalive

A voltage divider is used to feed the PSU's 12V output to the Raspberry Pi at ~3V. This is used to detect when the PSU is turned off so that the LCD can be shut off too. This is necessary because the RPi is powered by USB power, which stays on when the rest of the PC is off. The RPi uses the keepalive to detect when the PC turns off so it can shut off the LCD accordingly.

## Pin Layout

### Raspberry Pi

Specified pin numbers use the hardware pin numbering system.

| Purpose        | Pin # |
| -------------- | ----- |
| Motor HAT 3.3V | 1     |
| Motor HAT I2C  | 3,5   |
| LCD 5V         | 4     |
| LCD GND        | 6     |
| LCD TX         | 8     |
| PSU Power In   | 7     |

### Motor HAT

Each motor controller has two pins: `x` and `x'`, which are the two ouputs of the H-bridge.

| Purpose | Pin # |
| ------- | ----- |
| Red     | 3     |
| Green   | 1     |
| Blue    | 2     |
