package me.lucaspickering.casecontrol;

public final class ModeThread extends Thread {

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
    while (runLoop) {
      final Data data = CaseControl.getData();
      data.caseColor = data.caseMode.getColor();
      data.lcdColor = data.lcdMode.getColor();
      data.lcdText = data.lcdMode.getText();
      try {
        Thread.sleep(Data.MODE_LOOP_TIME);
      } catch (InterruptedException e) {
        e.printStackTrace();
      }
    }
  }
}
