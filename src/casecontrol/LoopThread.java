package casecontrol;

import java.awt.*;

import jssc.SerialPort;
import jssc.SerialPortException;

public final class LoopThread extends Thread {

  private final SerialPort serialPort = new SerialPort("COM3");
  private boolean runLoop;

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
          Color caseColor = CaseControl.getData().caseMode.getColor();
          Color lcdColor = CaseControl.getData().lcdMode.getColor();
          serialPort.writeBytes(new byte[]{
                  (byte) caseColor.getRed(), (byte) caseColor.getGreen(),
                  (byte) caseColor.getBlue(),
                  (byte) lcdColor.getRed(), (byte) lcdColor.getGreen(), (byte) lcdColor.getBlue()});

          String[] text = CaseControl.getData().lcdMode.getText();
          for (String line : text) {
            if (line.length() > Data.LCD_WIDTH) {
              line = line.substring(0, Data.LCD_WIDTH);
            }
            serialPort.writeString(line + "\n");
          }
          try {
            Thread.sleep(Data.LOOP_TIME);
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
      serialPort.writeBytes(new byte[]{0, 0, 0, 0, 0, 0});
      serialPort.closePort();
    } catch (SerialPortException e) {
      e.printStackTrace();
    }
  }
}
