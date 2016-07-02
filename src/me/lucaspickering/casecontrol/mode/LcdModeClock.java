package me.lucaspickering.casecontrol.mode;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

import me.lucaspickering.casecontrol.Data;
import me.lucaspickering.casecontrol.Funcs;

public final class LcdModeClock extends AbstractLcdMode {

	private static final DateFormat DATE = new SimpleDateFormat("EEEE, MMM d");
	private static final DateFormat HOURS = new SimpleDateFormat("h");
	private static final DateFormat MINUTES = new SimpleDateFormat("mm");
	private static final DateFormat SECONDS = new SimpleDateFormat("ss");

	@Override
	public String[] getText() {
		final Date date = new Date();
		final String today = DATE.format(date);
		text[0] = today + Funcs.padLeft(SECONDS.format(date), Data.LCD_WIDTH - today.length());

		final String hours = HOURS.format(date);
		final String minutes = MINUTES.format(date);
		String time;
		if (hours.length() == 1) {
			time = String.format("     %s : %s %s", hours, minutes.charAt(0), minutes.charAt(1));
		} else {
			time = String.format(" %s %s : %s %s", hours.charAt(0), hours.charAt(1),
													 minutes.charAt(0), minutes.charAt(1));
		}
		Funcs.addBigText(text, 1, time);

		return text;
	}

	@Override
	public String toString() {
		return "Clock";
	}
}
