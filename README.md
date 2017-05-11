# Case-Control-CLI
CLI to control the LEDs and LCD in my computer case. Interfaces with an Arduino Uno over a serial connection.

The LCD is a WH2004A-CFH-JT# with an HD44780-compatible driver. The LCD is used in 4-bit mode, meaning only 4 of the 8 data lines are used (see the charts below).

By default, the serial buffer on an Arduino Uno is only 64 bytes, which isn't enough for us. The file HardwareSerial.h is modified to increase the buffer to 128 bytes. Drop that file into "C:\Program Files (x86)\Arduino\hardware\arduino\avr\cores" (or something like that) to make it work.

### Arduino Pin Layout
This lays out what each used pin on the Arduino is connected to.

Pin #|Purpose
:---:|---
2 |LCD RS
3 |LCD Red
4 |LCD EN
5 |LCD Green
6 |LCD Blue
7 |LCD Data 4
8 |LCD Data 5
9 |LED Red
10|LED Green
11|LED Blue
12|LCD Data 6
13|LCD Data 7

### LCD Pin Layout
This lays out what each pin on the LCD is connected to on the Arduino. They are in left-to-right order when looking at the LCD from the back.

LCD|Arduino
---|---
GND|GND
5V|5V
Constrast|GND
RS|Pin 2
R/W|GND
EN|Pin 4
Data 0|-
Data 1|-
Data 2|-
Data 3|-
Data 4|Pin 7
Data 5|Pin 8
Data 6|Pin 12
Data 7|Pin 13
Backlight +|5V
Backlight Red|Pin 3
Backlight Green|Pin 5
Backlight Blue|Pin 6