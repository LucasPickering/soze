package me.lucaspickering.casecontrol;

import java.awt.*;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.lang.reflect.Field;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

public final class Funcs {

	private static final String HBR = "\u0001";
	private static final String HBL = "\u0002";
	private static final String BOT = "\u0003";
	private static final String FBR = "\u0004";
	private static final String FBL = "\u0005";
	private static final String FUL = "\u00ff";
	private static final String EMT = "\u0020";

	private static final String[] BIG_0 = new String[]{HBR + BOT + HBL,
																										 FUL + EMT + FUL,
																										 FBR + BOT + FBL};
	private static final String[] BIG_1 = new String[]{BOT + HBL + EMT,
																										 EMT + FUL + EMT,
																										 BOT + FUL + BOT};
	private static final String[] BIG_2 = new String[]{HBR + BOT + HBL,
																										 HBR + BOT + FBL,
																										 FBR + BOT + BOT};
	private static final String[] BIG_3 = new String[]{HBR + BOT + HBL,
																										 EMT + BOT + FUL,
																										 BOT + BOT + FBL};
	private static final String[] BIG_4 = new String[]{BOT + EMT + BOT,
																										 FBR + BOT + FUL,
																										 EMT + EMT + FUL};
	private static final String[] BIG_5 = new String[]{BOT + BOT + BOT,
																										 FUL + BOT + HBL,
																										 BOT + BOT + FBL};
	private static final String[] BIG_6 = new String[]{HBR + BOT + HBL,
																										 FUL + BOT + HBL,
																										 FBR + BOT + FBL};
	private static final String[] BIG_7 = new String[]{BOT + BOT + BOT,
																										 EMT + HBR + FBL,
																										 EMT + FUL + EMT};
	private static final String[] BIG_8 = new String[]{HBR + BOT + HBL,
																										 FUL + BOT + FUL,
																										 FBR + BOT + FBL};
	private static final String[] BIG_9 = new String[]{HBR + BOT + HBL,
																										 FBR + BOT + FUL,
																										 EMT + EMT + FUL};
	private static final String[] BIG_COLON = new String[]{FUL, EMT, FUL};
	private static final String[] BIG_SPACE = new String[]{EMT, EMT, EMT};

	private static DateFormat TEMPS_DATE_FORMAT = new SimpleDateFormat("YYYYMMdd");

	/**
	 * Clamps the given number to the given range.
	 *
	 * @param n   the number to be clamped
	 * @param min the minimum of the range (inclusive)
	 * @param max the maximum of the range (inclusive)
	 * @return n clamped to the range [0, 255]
	 */
	public static int clamp(int n, int min, int max) {
		return n < min ? min : n > max ? max : n;
	}

	/**
	 * Gets a color from a string. The string can either be an RGB set separated by '/', (e.g.
	 * 255/255/255 for white), or an alias (e.g. "white" for white). Valid aliases are all pre-defined
	 * colors in {@link java.awt.Color}. {@code s} is not case-sensitive.
	 *
	 * @param s the RGB value set or alias for the color
	 */
	public static Color getColor(String s) {
		String[] rgbSet = s.split("/");
		if (rgbSet.length == 1) {
			try {
				Field colorField = Color.class.getField(s.toUpperCase());
				return (Color) colorField.get(Color.BLACK);
			} catch (Exception e) {
				System.out.println(s + " is not a valid color.");
			}
		} else if (rgbSet.length >= 3) {
			try {
				int red = clamp(new Integer(rgbSet[0]), 0, 255);
				int green = clamp(new Integer(rgbSet[1]), 0, 255);
				int blue = clamp(new Integer(rgbSet[2]), 0, 255);
				return new Color(red, green, blue);
			} catch (NumberFormatException e) {
				System.out.println("Invalid RGB set. Arguments must be numbers.");
			}
		}
		System.out.println("Invalid argument. Only RGB sets and color aliases are accepted.");
		return null;
	}

	/**
	 * Adds the characters needed to write {@code text} in 3-line-tall characters to the given buffer.
	 * 3 lines of the buffer will be filled, starting at {@code offset}.
	 *
	 * @param buffer the string array to be added to
	 * @param offset the line of {@code buffer} to start the adding at
	 * @param text   the text to be written
	 */
	public static void addBigText(String[] buffer, int offset, String text) {
		final StringBuilder[] builders = new StringBuilder[3];
		for (char c : text.toCharArray()) {
			String[] newText = getBigChar(c);
			for (int i = 0; i < builders.length; i++) {
				if (builders[i] == null) {
					builders[i] = new StringBuilder();
				}
				builders[i].append(newText[i]);
			}
		}
		for (int i = 0; i < builders.length; i++) {
			buffer[offset + i] = builders[i].toString();
		}
	}

	/**
	 * Gets a string array representing a big character.
	 *
	 * @param c the character to be represented
	 * @return a 3-element string array representing a big character
	 */
	private static String[] getBigChar(char c) {
		switch (c) {
			case '0':
				return BIG_0;
			case '1':
				return BIG_1;
			case '2':
				return BIG_2;
			case '3':
				return BIG_3;
			case '4':
				return BIG_4;
			case '5':
				return BIG_5;
			case '6':
				return BIG_6;
			case '7':
				return BIG_7;
			case '8':
				return BIG_8;
			case '9':
				return BIG_9;
			case ':':
				return BIG_COLON;
			case ' ':
				return BIG_SPACE;
			default:
				throw new IllegalArgumentException(c + " is not a recognized big character");
		}
	}

	/**
	 * Pads a string with spaces on the left side to make it the given length.
	 *
	 * @param s      the string to be padded
	 * @param length the length to be padded to
	 */
	public static String padLeft(String s, int length) {
		return String.format("%1$" + length + "s", s);
	}

	/**
	 * Gets the last line of a file.
	 *
	 * @param file the file to be parsed (non-null)
	 * @return the last line, or an empty string if the file does not exist or is empty
	 * @throws NullPointerException if {@code file} is {@code null}
	 */
	private static String getLastLine(File file) {
		String lastLine = "";
		if (file.exists()) {
			try {
				BufferedReader reader = new BufferedReader(new FileReader(file));
				String tmp;

				while ((tmp = reader.readLine()) != null) {
					lastLine = tmp;
				}

				reader.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		return lastLine;
	}

	/**
	 * Gets the file from which SpeedFan temps should be read.
	 *
	 * @return the file to read temps from, which may or may not exist
	 */
	private static File getTempsFile() {
		return new File(String.format(Data.TEMPS_FILE, TEMPS_DATE_FORMAT.format(new Date())));
	}

	/**
	 * Gets the  4 CPU core temps, the GPU temp, & CPU fan speed from SpeedFan.
	 *
	 * @return an array of the data in RPM/degrees Celcius, in the following order: <ul> <li>CPU
	 * 1</li> <li>CPU 2</li> <li>CPU 3</li> <li>CPU 4</li> <li>GPU</li> <li>CPU Fan Speed</li> </ul>
	 */
	public static int[] getSpeedFanData() {
		final String[] pieces = getLastLine(getTempsFile()).split("\t");
		final int[] data = new int[6];

		for (int i = 1; i < pieces.length; i++) {
			data[i - 1] = new Float(pieces[i]).intValue();
		}

		return data;
	}

	public static void pause(long ms) {
		try {
			Thread.sleep(ms);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}

	public static String padRight(String s, int n) {
		return String.format("%1$-" + n + "s", s);
	}
}
