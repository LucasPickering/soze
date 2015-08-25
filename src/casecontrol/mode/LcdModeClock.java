package casecontrol.mode;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

import casecontrol.Data;
import casecontrol.Funcs;

public final class LcdModeClock extends AbstractLcdMode {

  private static final DateFormat LONG_DATE = new SimpleDateFormat("dddd, MMMM d");
  private static final DateFormat SHORT_DATE = new SimpleDateFormat("dddd, MMM d");
  private static final DateFormat HOURS = new SimpleDateFormat("HH");
  private static final DateFormat MINUTES = new SimpleDateFormat("mm");
  private static final DateFormat SECONDS = new SimpleDateFormat("ss");

  @Override
  public String[] getText() {
    final Date date = new Date();
    String today = LONG_DATE.format(date);
    if (today.length() > Data.LCD_WIDTH - 3) {
      today = SHORT_DATE.format(date);
    }
    text[0] = today + Funcs.padLeft(SECONDS.format(date), Data.LCD_WIDTH - today.length());

    final String hours = HOURS.format(date);
    final String minutes = MINUTES.format(date);
    Funcs.addBigText(text, 1, String.format(" %s %s : %s %s", hours.charAt(0), hours.charAt(1),
                                            minutes.charAt(0), minutes.charAt(1)));

    return text;
  }
}
