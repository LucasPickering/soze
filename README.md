# Case-Control-CLI
CLI to control the LEDs and LCD in my computer case. Interfaces with an Arduino Uno over a serial connection.

By default, the serial buffer on an Arduino Uno is only 64 bytes, which isn't enough for us. The file HardwareSerial.h is modified to increase the buffer to 128 bytes. Drop that file into "C:\Program Files (x86)\Arduino\hardware\arduino\avr\cores" (or something like that) to make it work.

Uses the [jSSC library](https://code.google.com/p/java-simple-serial-connector/) for serial connections.  
