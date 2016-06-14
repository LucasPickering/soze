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

const int BAUD_RATE = 57600;

const int TIMEOUT = 3000;

const int MIN_PACKET_SIZE = 4;
const char CASE_COLOR_TAG = 'c';
const char LCD_COLOR_TAG = 'l';
const char LCD_TEXT_TAG = 't';

LiquidCrystal lcd(2, 4, 7, 8, 12, 13);
String lcdText[LCD_HEIGHT];
SimpleTimer timer;
int timerId;

void serialFlush(){
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
}

void setCaseColor(byte red, byte green, byte blue) {
  analogWrite(CASE_RED, red);
  analogWrite(CASE_GREEN, green);
  analogWrite(CASE_BLUE, blue);
}

void setLcdColor(byte red, byte green, byte blue) {
  analogWrite(LCD_RED, 255 - red);
  analogWrite(LCD_GREEN, 255 - green);
  analogWrite(LCD_BLUE, 255 - blue);
}

void turnOff() {
  setCaseColor(0, 0, 0);
  setLcdColor(0, 0, 0);
  lcd.clear();
}

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
  Serial.begin(57600);

  timerId = timer.setInterval(TIMEOUT, turnOff);
}

void loop() {
  timer.run(); // The timer to track when a timeout should occur
  if (Serial.available() >= 4) {
    timer.restartTimer(timerId); // Reset the timeout
    char tag = Serial.read(); // Read the first byte (the tag)
    byte bytesRead = 1; // Start at 1 to account for the tag
    switch(tag) {
      case CASE_COLOR_TAG:
      {
        // Set case color
        // These variables are needed to make sure the colors get read in the right order
        byte red = Serial.read();
        byte green = Serial.read();
        byte blue = Serial.read();
        setCaseColor(red, green, blue);
        bytesRead += 3; // 3 colors
        break;
      }
      case LCD_COLOR_TAG:
      {
        // Set LCD color
        // These variables are needed to make sure the colors get read in the right order
        byte red = Serial.read();
        byte green = Serial.read();
        byte blue = Serial.read();
        setLcdColor(red, green, blue);
        bytesRead += 3; // 3 colors
        break;
      }
      case LCD_TEXT_TAG:
        // Set LCD text
        // For each line on the lcd
        for(int line = 0; line < LCD_HEIGHT; line++) {
          lcd.setCursor(0, line); // Set the lcd cursor to the start of this line
          String textLine = lcdText[line];
          
          for(int col = 0; col < LCD_WIDTH; col++) {
            char newChar = Serial.read();
            bytesRead++;
            // If this character is different from the one already there, update it
            if(newChar != textLine[col]) {
              textLine.setCharAt(col, newChar); // Update the array
              lcd.write(newChar); // Update the LCD
            }
          }
        }
        break;
      default:
        // Something other than a tag showed up. Not good.
        serialFlush(); // Clear the buffer
        bytesRead = tag;
        break;
    }
    
    Serial.write(bytesRead); // Send a confirmation message
  }
}
