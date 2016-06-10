package me.lucaspickering.casecontrol;

import java.awt.*;
import java.util.Arrays;

import jssc.SerialPort;
import jssc.SerialPortException;

public final class SerialThread extends Thread {

  private final SerialPort serialPort = new SerialPort("COM3");
  private boolean runLoop;

  // Those hold the last values sent to the Arduino. New values are only sent when they differ from
  // these old values.
  private Color lastCaseColor = Color.BLACK;
  private Color lastLcdColor = Color.BLACK;
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

          // If the case color changed, update it.
          if (!data.caseColor.equals(lastCaseColor)) {
            writeColor(PacketTag.CASE_COLOR.tag, data.caseColor);
            lastCaseColor = data.caseColor;
          }

          // If the LCD color changed, update it.
          if (!data.lcdColor.equals(lastLcdColor)) {
            writeColor(PacketTag.LCD_COLOR.tag, data.lcdColor);
            lastLcdColor = data.lcdColor;
          }

          // If the LCD text changed, update it.
          if (!Arrays.equals(lastLcdText, data.lcdText)) {
            serialPort.writeByte((byte) PacketTag.LCD_TEXT.tag); // Tell the Arduino words are coming
            // For each line in the text...
            for (String line : data.lcdText) {
              // If the line is too long for the LCD, chop it down
              if (line.length() > Data.LCD_WIDTH) {
                line = line.substring(0, Data.LCD_WIDTH);
              }
              serialPort.writeString(line + "\n"); // Write the line, with a newline char at the end
            }
            System.arraycopy(data.lcdText, 0, lastLcdText, 0, data.lcdText.length);
          }

          // Try to pause to let the Arduino read
          try {
            Thread.sleep(Data.SERIAL_LOOP_TIME);
          } catch (InterruptedException e) {
            e.printStackTrace();
          }
        } else {
          serialPort.openPort(); // Open the port because it isn't already
          serialPort.setParams(115200, 8, 1, 0); // 115200 bps, 8 data bits, 1 stop bit, no parity
          try {
            Thread.sleep(3000);
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

  private void writeColor(char tag, Color color) throws SerialPortException {
    serialPort.writeBytes(new byte[]{
        (byte) tag, (byte) color.getRed(), (byte) color.getGreen(), (byte) color.getBlue()});
  }
}
