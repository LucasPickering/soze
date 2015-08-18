package casecontrol;

import java.awt.*;

import jssc.SerialPort;
import jssc.SerialPortException;

public final class LoopThread extends Thread {

  private final SerialPort serialPort = new SerialPort("COM3");
  private boolean runLoop;

  public LoopThread() {
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
        if (serialPort.isOpened()) {
          Color caseColor = Data.caseMode.getColor();
          Color lcdColor = Data.lcdMode.getColor();
          String[] text = Data.lcdMode.getText();
          byte[] colorData = new byte[]{(byte) caseColor.getRed(), (byte) caseColor.getGreen(),
              (byte) caseColor.getBlue(), (byte) lcdColor.getRed(),
              (byte) lcdColor.getGreen(), (byte) lcdColor.getBlue()};
          serialPort.writeBytes(colorData);
          try {
            Thread.sleep(30);
          } catch (InterruptedException e) {
            e.printStackTrace();
          }
        } else {
          serialPort.openPort();
          serialPort.setParams(115200, 8, 1, 0);
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
}
