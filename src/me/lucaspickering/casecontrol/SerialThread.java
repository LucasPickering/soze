package me.lucaspickering.casecontrol;

import java.awt.*;
import java.util.Arrays;

import jssc.SerialPort;
import jssc.SerialPortException;
import jssc.SerialPortTimeoutException;

public final class SerialThread extends Thread {

  private static final int STARTUP_TIME = 2000;
  private static final int LOOP_TIME = 1000;
  private static final int BAUD_RATE = 57600;
  private static final int DATA_BITS = 8;
  private static final int STOP_BITS = 1;
  private static final int PARITY = 0;

  private final SerialPort serialPort = new SerialPort("COM3");
  private boolean runLoop;

  // Those hold the last values sent to the Arduino. New values are only sent when they differ from
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
    try {
      while (runLoop) {
        // If the port is open, write data
        if (serialPort.isOpened()) {
          final Data data = CaseControl.getData(); // The data to be written

          waitForAck(writeCaseColor(data)); // Write case color and wait for ack message
          waitForAck(writeLcdColor(data)); // Write LCD color and wait for ack message
          waitForAck(writeText(data)); // Write LCD text and wait for ack message

          /*
          // Pause for a bit
          try {
            Thread.sleep(LOOP_TIME);
          } catch (InterruptedException e) {
            e.printStackTrace();
          }*/
        } else {
          serialPort.openPort(); // Open the port because it isn't already
          serialPort.setParams(BAUD_RATE, DATA_BITS, STOP_BITS, PARITY);

          // Pause to let the serial port set up
          try {
            Thread.sleep(STARTUP_TIME);
          } catch (InterruptedException e) {
            e.printStackTrace();
          }
        }
      }
      serialPort.closePort();
    } catch (SerialPortException e) {
      e.printStackTrace();
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
        serialPort.writeString(line); // Write the line
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
        byte ack = serialPort.readBytes(1, 1000)[0];
        System.out.println(String.format("Should be %d. Was %d.", bytesExpected, ack)); // TODO: DEL
        if(ack != bytesExpected) {
          System.err.println(String.format("Error! Expected ACK of %d but received %d!",
                                           bytesExpected, ack));
        }
      } catch (SerialPortTimeoutException e) {
        e.printStackTrace();
      }
    }
  }

  private static String padRight(String s, int n) {
    return String.format("%1$-" + n + "s", s);
  }
}
