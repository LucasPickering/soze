package casecontrol.mode;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

import casecontrol.Data;

public final class LcdModeTodo extends AbstractLcdMode {

  @Override
  public String[] getText() {
    try {
      BufferedReader reader = new BufferedReader(new FileReader("todo.txt"));
      String line;
      for (int i = 0; i < Data.LCD_HEIGHT && (line = reader.readLine()) != null; i++) {
        if(line.length() > Data.LCD_WIDTH) {
          line = line.substring(0, Data.LCD_WIDTH);
        }
        text[i] = line;
      }
    } catch (IOException e) {
      e.printStackTrace();
    }
    return text;
  }
}
