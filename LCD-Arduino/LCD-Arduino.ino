#include <LiquidCrystal.h>

// Pin numbers are defined here - see README.md for a pretty chart of what each pin does
const int CASE_RED = 9;
const int CASE_GREEN = 10;
const int CASE_BLUE = 11;

const int LCD_RED = 3;
const int LCD_GREEN = 5;
const int LCD_BLUE = 6;

const int LCD_RS = 2;
const int LCD_EN = 4;
const int LCD_D4 = 7;
const int LCD_D5 = 8;
const int LCD_D6 = 12;
const int LCD_D7 = 13;

// LCD dimensions, in characters
const int LCD_WIDTH = 20;
const int LCD_HEIGHT = 4;

// Special characters for the LCD, used to make big numbers
const int HBR = 1; // Half bottom right
const int HBL = 2; // Half bottom right
const int BOT = 3; // Bottom
const int FBR = 4; // Full bottom right
const int FBL = 5; // Full bottom left
const int FUL = 255; // Full rect

const long BAUD_RATE = 57600;

const int TIMEOUT = 3000;

const int MIN_PACKET_SIZE = 4;
const char CASE_COLOR_TAG = 'c';
const char LCD_COLOR_TAG = 'l';
const char LCD_TEXT_TAG = 't';

LiquidCrystal lcd(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7);
String lcdText[LCD_HEIGHT]; // This always holds the exact text that is displayed on the LCD
int timerId;
unsigned long lastReceiveTime = 0;

// Flushes all data from the serial buffer
void serialFlush(){
    while(Serial.available() > 0) {
        char t = Serial.read();
    }
}

// Reads a color from the serial buffer and puts its components into the given variables
void readColor(byte& red, byte& green, byte& blue) {
    red = Serial.read();
    green = Serial.read();
    blue = Serial.read();
}

// Sets the color of the case LEDs
void setCaseColor(byte const& red, byte const& green, byte const& blue) {
    analogWrite(CASE_RED, red);
    analogWrite(CASE_GREEN, green);
    analogWrite(CASE_BLUE, blue);
}

// Sets the color of the LCD backlight
void setLcdColor(byte const& red, byte const& green, byte const& blue) {
    analogWrite(LCD_RED, 255 - red);
    analogWrite(LCD_GREEN, 255 - green);
    analogWrite(LCD_BLUE, 255 - blue);
}

// Reads character values from serial and updates the LCD if they differ from what is currently
// being displayed
void updateLCD() {
    // For each line on the LCD...
    for(int line = 0; line < LCD_HEIGHT; line++) {
        String textLine = lcdText[line]; // Get the string for this line
        lcd.setCursor(0, line); // Set the LCD cursor to the start of this line

        // For each character in the line...
        for(int col = 0; col < LCD_WIDTH; col++) {
            char newChar = Serial.read(); // Read the next character from the serial buffer
            // If this character is different from the one in the array, update it
            if(newChar != textLine[col]) {
                textLine.setCharAt(col, newChar); // Update the array
                lcd.write(newChar); // Update the LCD
            }
        }
    }
}

// Turns the LCD and LEDs off
void turnOff() {
    setCaseColor(0, 0, 0);
    setLcdColor(0, 0, 0);
    lcd.clear();
}

void setup() {
    // Set pin modes for LED and LCD backlight pins - these will be PWM
    pinMode(CASE_RED, OUTPUT);
    pinMode(CASE_GREEN, OUTPUT);
    pinMode(CASE_BLUE, OUTPUT);

    pinMode(LCD_RED, OUTPUT);
    pinMode(LCD_GREEN, OUTPUT);
    pinMode(LCD_BLUE, OUTPUT);

    setLcdColor(B0, B0, B0); // Turn the LCD backlight off

    // Define custom characters for the LCD
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

    // Start the LCD and serial connection
    lcd.begin(LCD_WIDTH, LCD_HEIGHT);
    Serial.begin(BAUD_RATE);
}

void loop() {
    if (Serial.available() >= 4) {
        char tag = Serial.read(); // Read the first byte (the tag)
        // These will be needed later if a color is read from serial
        byte red;
        byte green;
        byte blue;
        switch(tag) {
            case CASE_COLOR_TAG:
                // Set case color
                readColor(red, green, blue); // Read values from serial into the variables
                setCaseColor(red, green, blue); // Write values to the case LEDs
                break;
            case LCD_COLOR_TAG:
                // Set LCD color
                readColor(red, green, blue); // Read values from serial into the variables
                setLcdColor(red, green, blue); // Write values to the LCD backlight
                break;
            case LCD_TEXT_TAG:
                // Update LCD text
                updateLCD();
                break;
            default:
                // Something other than a tag showed up. Not good.
                serialFlush(); // Clear the buffer
                break;
        }
        lastReceiveTime = millis();
    }

    // If we haven't received a message in the last TIMEOUT ms, turn off the LCD/LEDs
    if(millis() - lastReceiveTime >= TIMEOUT) {
        turnOff();
    }
}
