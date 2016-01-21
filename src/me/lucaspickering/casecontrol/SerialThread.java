package me.lucaspickering.casecontrol;

import jssc.SerialPort;
import jssc.SerialPortException;

public final class SerialThread extends Thread {

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
          final Data data = CaseControl.getData();

          serialPort.writeBytes(new byte[]{
                  (byte) data.caseColor.getRed(), (byte) data.caseColor.getGreen(),
                  (byte) data.caseColor.getBlue(),
                  (byte) data.lcdColor.getRed(), (byte) data.lcdColor.getGreen(),
                  (byte) data.lcdColor.getBlue()});

          for (String line : data.lcdText) {
            if (line.length() > Data.LCD_WIDTH) {
              line = line.substring(0, Data.LCD_WIDTH);
            }
            serialPort.writeString(line + "\n");
          }
          try {
            Thread.sleep(Data.SERIAL_LOOP_TIME);
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
