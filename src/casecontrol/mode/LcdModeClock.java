package casecontrol.mode;

import java.text.SimpleDateFormat;
import java.util.Date;

import casecontrol.Data;
import casecontrol.Funcs;

public final class LcdModeClock extends AbstractLcdMode {

  @Override
  public String[] getText() {
    Date date = new Date();
    String today = new SimpleDateFormat("dddd, MMMM d").format(date);
    if (today.length() > Data.LCD_WIDTH - 3) {
      today = new SimpleDateFormat("dddd, MMM d").format(date);
    }
    text[0] = today + Funcs.padLeft(new SimpleDateFormat("ss").format(date),
                                    Data.LCD_WIDTH - today.length());

    String hours = new SimpleDateFormat("HH").format(date);
    String minutes = new SimpleDateFormat("mm").format(date);
    Funcs.addBigText(text, 1, String.format(" %s %s : %s %s", hours.charAt(0), hours.charAt(1),
                                            minutes.charAt(0), minutes.charAt(1)));

    return text;
  }
}
