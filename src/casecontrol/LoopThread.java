package casecontrol;

import org.zu.ardulink.Link;

import java.awt.*;

public final class LoopThread extends Thread {

  private final Link link;
  private boolean runLoop;

  public LoopThread() {
    link = Link.createInstance("arduino");
    if (!link.connect("COM3", 115200)) {
      System.err.println("Could not open serial connection");
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
      Color caseColor = Data.caseMode.getColor();
      Color lcdColor = Data.lcdMode.getColor();
      String[] text = Data.lcdMode.getText();
      int[] colorData = new int[]{caseColor.getRed(), caseColor.getGreen(), caseColor.getBlue(),
          lcdColor.getRed(), lcdColor.getGreen(), lcdColor.getBlue()};
      link.writeSerial(colorData.length, colorData);
      try {
        Thread.sleep(30);
      } catch (InterruptedException e) {
        System.err.println("Sleep was interrupted");
      }
    }
    link.disconnect();
    System.out.println("Loop stopped");
  }
}
