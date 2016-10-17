package me.lucaspickering.casecontrol;

import me.lucaspickering.casecontrol.mode.caseled.CaseMode;
import me.lucaspickering.casecontrol.mode.lcd.LcdMode;

public final class ModeThread extends Thread {

    private boolean runLoop;
    private CaseMode caseMode;
    private LcdMode lcdMode;

    @Override
    public void start() {
        runLoop = true; // Do our initialization before starting up
        super.start();
    }

    public void terminate() {
        runLoop = false;
    }

    @Override
    public void run() {
        while (runLoop) {
            // All this does is call the get functions, which do the processing for color/text
            final Data data = CaseControl.getData();

            try {
                // Update case/LCD modes, if necessary
                updateModes();
            } catch (InstantiationException | IllegalAccessException e) {
                e.printStackTrace();
            }

            data.caseColor = caseMode.getColor();
            data.lcdColor = lcdMode.getColor();
            data.lcdText = lcdMode.getText();
            try {
                Thread.sleep(Data.MODE_LOOP_TIME);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    private void updateModes() throws InstantiationException, IllegalAccessException {
        final Data data = CaseControl.getData();
        if (caseMode == null || caseMode.getMode() != data.caseMode) {
            caseMode = data.caseMode.clazz.newInstance(); // If the case mode changed, update it
        }
        if (lcdMode == null || lcdMode.getMode() != data.lcdMode) {
            lcdMode = data.lcdMode.clazz.newInstance(); // If the LCD mode changed, update it
        }
    }
}
