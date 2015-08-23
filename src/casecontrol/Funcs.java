package casecontrol;

import java.awt.Color;
import java.lang.reflect.Field;

public final class Funcs {

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
}
