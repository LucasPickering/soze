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

### Webapp (TypeScript)

A React-based webpage that exposes configuration. This is just a few pretty controls that visualize the user state. Generates HTTP requests to get and update user state. Runs from a webserver (Nginx) on the RPi, but this could run on any machine with network access to the RPi.

## Installation

### Development

There are two ways of running this in development:

#### Terminal Mock Display

This is the typical way to run during development. This mocks the entire display with a terminal program that renders LED and LCD data live. This is useful for UI/api/reducer development because it's easy and visual, but it **completely bypasses the code in `hw_display/`.**

If this is your first time running it, you'll need to install some Python dependencies. Feel free to use your preferred virtualenv solution, and run:

```
pip install -r mock_display/requirements.txt
```

Then to fire it up, run this in one terminal window:

```
docker-compose up
```

and run this in another:

```
cd mock_display
python3 -m soze_display
```

Docker Compose will run all the services (webapp, API, reducer, Redis) that you need. The mock display has to be run separately because it runs a curses output that doesn't play nice with docker compose.

#### Hardware Display w/ Mock Libraries

If you need to test code from `hw_display/`, there are mocks for the hardware libraries that you can use. The hardware output is just logged to files instead of being visual.

```
docker-compose -f docker-compose.hw-display.yml up
```

Then the log files with the hardware output will all be in `hw_display/mock_logs/`.

### Production

All Docker images are built locally, using `docker buildx` for cross-building and `docker buildx bake` to replace `docker-compose build`. [See here](https://www.docker.com/blog/multi-platform-docker-builds/) for info on cross builds. After being built, images are pushed to GitHub's container registry.

#### Build

First, you'll need to log in to `ghcr.io` to push images. [See here](https://docs.github.com/en/packages/guides/configuring-docker-for-use-with-github-packages#authenticating-to-github-packages).

Then, run this **on your dev machine** (it may take a long time):

```sh
./scripts/build_and_push.sh
```

If you change just a single component and want to avoid rebuilding all of them, you can pass individual targets, like so:

```sh
./scripts/build_and_push.sh api display
```

#### Deploy

Start the docker-compose stack on the Pi with:

```sh
./scripts/deploy.sh pi@<host>
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
