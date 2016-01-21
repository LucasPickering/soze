#include <LiquidCrystal.h>
#include "SimpleTimer.h"

const int CASE_RED = 9;
const int CASE_GREEN = 10;
const int CASE_BLUE = 11;

const int LCD_RED = 3;
const int LCD_GREEN = 5;
const int LCD_BLUE = 6;

const int LCD_WIDTH = 20;
const int LCD_HEIGHT = 4;

const int HBR = 1;
const int HBL = 2;
const int BOT = 3;
const int FBR = 4;
const int FBL = 5;
const int FUL = 255;
const int EMT = 32;

const int TIMEOUT = 3000;

LiquidCrystal lcd(2, 4, 7, 8, 12, 13);
String lcdText[LCD_HEIGHT];
SimpleTimer timer;
int timerId;

/*
 Serial Data is sent in packets of 6+ bytes
 0  - LED Red
 1  - LED Green
 2  - LED Blue
 3  - LCD Red
 4  - LCD Green
 5  - LCD Blue
 6+ - Text to be written to the LCD
*/

void setup() {
  pinMode(CASE_RED, OUTPUT);
  pinMode(CASE_GREEN, OUTPUT);
  pinMode(CASE_BLUE, OUTPUT);
  
  pinMode(LCD_RED, OUTPUT);
  pinMode(LCD_GREEN, OUTPUT);
  pinMode(LCD_BLUE, OUTPUT);
  
  analogWrite(LCD_RED, 255);
  analogWrite(LCD_GREEN, 255);
  analogWrite(LCD_BLUE, 255);
  
  byte hbrBytes[] = { B00000, B00000, B00000, B00000, B00011, B01111, B01111, B11111 };
  lcd.createChar(HBR, hbrBytes);
  
  byte hblBytes[] = { B00000, B00000, B00000, B00000, B11000, B11110, B11110, B11111 };
  lcd.createChar(HBL, hblBytes);
  
  byte botBytes[] = { B00000, B00000, B00000, B00000, B11111, B11111, B11111, B11111 };
  lcd.createChar(BOT, botBytes);
  
  byte fbrBytes[] = { B11111, B11111, B11111, B11111, B11111, B01111, B01111, B00011 };
  lcd.createChar(FBR, fbrBytes);
  
  byte fblBytes[] = { B11111, B11111, B11111, B11111, B11111, B11110, B11110, B11000 };
  lcd.createChar(FBL, fblBytes);
  
  lcd.begin(LCD_WIDTH, LCD_HEIGHT);
  Serial.begin(115200);

  timerId = timer.setInterval(TIMEOUT, turnOff);
}

void loop() {
  timer.run();
  if (Serial.available() >= 6) {
    // Serial packet received. Update 
    analogWrite(CASE_RED, Serial.read());
    analogWrite(CASE_GREEN, Serial.read());
    analogWrite(CASE_BLUE, Serial.read());
    
    analogWrite(LCD_RED, 255 - Serial.read());
    analogWrite(LCD_GREEN, 255 - Serial.read());
    analogWrite(LCD_BLUE, 255 - Serial.read());
    
    for(int line = 0; line < LCD_HEIGHT; line++) {
      lcd.setCursor(0, line);
      boolean newLine = false;
      String textLine = lcdText[line];
      
      for(int col = 0; col < LCD_WIDTH; col++) {
        char newChar = ' ';
        
        if(!newLine && Serial.available()) {
          newChar = Serial.read();
          if(newChar == '\n') {
            newLine = true;
            newChar = ' ';
          }
        }
        
        if(newChar != textLine[col]) {
          textLine.setCharAt(col, newChar);
          lcd.write(newChar);
        }
      }
      
      if(Serial.peek() == '\n') {
        Serial.read();
      }
    }

    timer.restartTimer(timerId);
  }
}

void turnOff() {
  /*
  analogWrite(CASE_RED, 255);
  analogWrite(CASE_GREEN, 0);
  analogWrite(CASE_BLUE, 0);
  */
  analogWrite(LCD_RED, 255);
  analogWrite(LCD_GREEN, 255);
  analogWrite(LCD_BLUE, 255);

  lcd.clear();
}
