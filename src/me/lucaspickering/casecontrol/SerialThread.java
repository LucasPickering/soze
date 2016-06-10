package me.lucaspickering.casecontrol;

import java.awt.*;

import jssc.SerialPort;
import jssc.SerialPortException;

public final class SerialThread extends Thread {

  private final SerialPort serialPort = new SerialPort("COM3");
  private boolean runLoop;
  private Data lastData;

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
          writeColors(data); // Write color data

          // Write LCD text data
          for (String line : data.lcdText) {
            // If the line is too long for the LCD, chop it down
            if (line.length() > Data.LCD_WIDTH) {
              line = line.substring(0, Data.LCD_WIDTH);
            }
            serialPort.writeString(line + "\n"); // Write the line, with a newline char
          }

          try {
            Thread.sleep(Data.SERIAL_LOOP_TIME); // Pause to let the Arduino read
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
      serialPort.writeBytes(new byte[6]); // Write zeros to turn everything off
      serialPort.closePort();
    } catch (SerialPortException e) {
      e.printStackTrace();
    }
  }

  private void writeColors(Data data) throws SerialPortException {
    Color caseColor = data.caseColor;
    Color lcdColor = data.lcdColor;
    serialPort.writeBytes(new byte[]{
        (byte) caseColor.getRed(), (byte) caseColor.getGreen(), (byte) caseColor.getBlue(),
        (byte) lcdColor.getRed(), (byte) lcdColor.getGreen(), (byte) lcdColor.getBlue()});
  }
}
