package casecontrol;

import java.awt.*;
import java.lang.reflect.Field;

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
    for (char c : text.toCharArray()) {
      String[] newText = getBigChar(c);
      for (int i = offset; i < buffer.length; i++) {
        buffer[i] += newText[i - offset];
      }
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
   * @param s the string to be padded
   * @param length the length to be padded to
   * @return
   */
  public static String padLeft(String s, int length) {
    return String.format("%1$#" + length + "s", s);
  }
}
