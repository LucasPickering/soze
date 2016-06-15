package me.lucaspickering.casecontrol;

import java.awt.*;
import java.util.Arrays;

import jssc.SerialPort;
import jssc.SerialPortException;
import jssc.SerialPortTimeoutException;

public final class SerialThread extends Thread {

  private static final int STARTUP_TIME = 2000;
  private static final int LOOP_TIME = 20;
  private static final int ACK_TIMEOUT = 1000;

  private static final int BAUD_RATE = 57600;
  private static final int DATA_BITS = 8;
  private static final int STOP_BITS = 1;
  private static final int PARITY = 0;

  private final SerialPort serialPort = new SerialPort("COM3");
  private boolean runLoop;

  // These hold the last values sent to the Arduino. New values are only sent when they differ from
  // these old values.
  private Color lastCaseColor = null;
  private Color lastLcdColor = null;
  private String[] lastLcdText = new String[Data.LCD_HEIGHT];

  private enum PacketTag {
    CASE_COLOR('c'), LCD_COLOR('l'), LCD_TEXT('t');

    private final char tag;

    PacketTag(char tag) {
      this.tag = tag;
    }
  }

  @Override
  public void start() {
    runLoop = true;
    super.start();
  }

  public void terminate() {
    runLoop = false;
  }

  @Override
  public void run() {
    while (runLoop) {
      // If the port isn't open, try to open it. Otherwise, send data.
      if (!serialPort.isOpened()) {
        try {
          serialPort.openPort(); // Open the port because it isn't already
          serialPort.setParams(BAUD_RATE, DATA_BITS, STOP_BITS, PARITY);
        } catch (SerialPortException e) {
          System.err.printf("Error opening serial port. Will try again in %d ms.\n", STARTUP_TIME);
        }

        // Pause to let the serial port set up (or before trying to open again
        try {
          Thread.sleep(STARTUP_TIME);
        } catch (InterruptedException e) {
          e.printStackTrace();
        }
      } else {
        final Data data = CaseControl.getData(); // The data to be written

        // Send all necessary data
        try {
          waitForAck(writeCaseColor(data)); // Write case color and wait for ack message
          waitForAck(writeLcdColor(data)); // Write LCD color and wait for ack message
          waitForAck(writeText(data)); // Write LCD text and wait for ack message
        } catch (SerialPortException e) {
          System.err.println("Error sending data over serial port.");
        }

        // Pause for a bit
        try {
          Thread.sleep(LOOP_TIME);
        } catch (InterruptedException e) {
          e.printStackTrace();
        }
      }
    }

    // Close the port
    try {
      serialPort.closePort();
    } catch (SerialPortException e) {
      System.err.println("Error closing serial port.");
    }
  }

  /**
   * Writes the current case color to the serial port, IF the color has changed since it was last
   * written.
   *
   * @param data the data containing the current case color
   * @return the number of bytes written to the stream
   */
  private int writeCaseColor(Data data) throws SerialPortException {
    // If the case color changed, update it.
    if (lastCaseColor == null || !data.caseColor.equals(lastCaseColor)) {
      writeColor(PacketTag.CASE_COLOR.tag, data.caseColor);
      lastCaseColor = data.caseColor;
      return 4;
    }
    return 0;
  }

  /**
   * Writes the current LCD color to the serial port, IF the color has changed since it was last
   * written.
   *
   * @param data the data containing the current LCD color
   * @return the number of bytes written to the stream
   */
  private int writeLcdColor(Data data) throws SerialPortException {
    // If the case color changed, update it.
    if (lastLcdColor == null || !data.lcdColor.equals(lastLcdColor)) {
      writeColor(PacketTag.LCD_COLOR.tag, data.lcdColor);
      lastLcdColor = data.lcdColor;
      return 4;
    }
    return 0;
  }

  /**
   * Writes the current LCD text to the serial port, IF the text has changed since it was last
   * written.
   *
   * @param data the data containing the current LCD text
   * @return the number of bytes written to the stream
   */
  private int writeText(Data data) throws SerialPortException {
    if (!Arrays.equals(lastLcdText, data.lcdText)) {
      int bytesWritten = 0;
      serialPort.writeByte((byte) PacketTag.LCD_TEXT.tag); // Tell the Arduino words are coming
      bytesWritten++; // Account for the tag byte

      // For each line in the text...
      for (String line : data.lcdText) {
        // If the line is too long for the LCD, chop it down.
        // If it's too short, pad it with spaces
        if (line.length() > Data.LCD_WIDTH) {
          line = line.substring(0, Data.LCD_WIDTH);
        } else if (line.length() < Data.LCD_WIDTH) {
          line = padRight(line, Data.LCD_WIDTH);
        }
        writeStringToSerial(line); // Write the line
        bytesWritten += line.length(); // Should always be Data.LCD_WIDTH
      }
      System.arraycopy(data.lcdText, 0, lastLcdText, 0, data.lcdText.length);
      return bytesWritten;
    }
    return 0;
  }

  private void writeColor(char tag, Color color) throws SerialPortException {
    serialPort.writeBytes(new byte[]{
        (byte) tag, (byte) color.getRed(), (byte) color.getGreen(), (byte) color.getBlue()});
  }

  /**
   * Waits for an acknowledge message from the serial port. The message code will be equal to the
   * number of bytes written to the stream since the last ACK was received. If {@code bytesExpected}
   * is zero, nothing happens.
   *
   * @param bytesExpected the code expected to come from the stream
   */
  private void waitForAck(int bytesExpected) throws SerialPortException {
    if (bytesExpected > 0) {
      try {
        byte ack = serialPort.readBytes(1, ACK_TIMEOUT)[0];
        if (ack != bytesExpected) {
          System.err.printf("Error! Expected ACK of %d but received %d!\n", bytesExpected, ack);
        }
      } catch (SerialPortTimeoutException e) {
        System.err.printf("No ACK received after %d ms\n", ACK_TIMEOUT);
      }
    }
  }

  private static String padRight(String s, int n) {
    return String.format("%1$-" + n + "s", s);
  }

  /**
   * Write the given string to the serial port. {@link SerialPort#writeString} wasn't working (but
   * only in IntelliJ) so I wrote this.
   *
   * I guess this is as good a place as any to describe the bug (so I don't run into it again, so here
   * goes:
   *
   * Under windows-1232 encoding, it works fine because it encodes characters into bytes exactly
   * according to the literal codes they're defined with, i.e. "\u00ff" will be decoded into 255 (or
   * more accurately, 0b11111111, which will print as -1 for a signed byte). BUT, under UTF-8, any
   * character with a code 128+ will be encoded as 2+ bytes, so when a string containing that
   * character gets decoded, that character will be represented by multiple bytes in the
   * array/buffer/etc. {@link SerialPort#writeString} uses {@link String#getBytes} and treats each
   * byte in the array as one character (why wouldn't it). Unfortunately, for any character with code
   * 128+ (not typically relevant because ASCII only goes to 127), it will start screwing up and
   * everything will get offset by one byte (or more). I could make {@link SerialPort#writeString}
   * work by forcing the default encoding to windows-1232, but I'm not sure how portable that is (will
   * Linux like that?) and as far as I can tell, the only way to do that is with a VM flag
   * (-Dfile.encoding=windows-1232) when the program starts, and having to remember to set up a VM
   * flag is dumb. If you're future me and you're reading this, you're welcome. If you're anyone else,
   * why the hell are you reading this?
   *
   * @param s the string to be written
   */
  private void writeStringToSerial(String s) throws SerialPortException {
    for (char c : s.toCharArray()) {
      serialPort.writeByte((byte) c);
    }
  }
}