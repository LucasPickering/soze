package me.lucaspickering.casecontrol;

import java.awt.*;
import java.util.Arrays;

import jssc.SerialPort;
import jssc.SerialPortException;

public final class SerialThread extends Thread {

    private static final int STARTUP_TIME = 2000;
    private static final int LOOP_TIME = 20;
    private static final int PING_FREQUENCY = 1500;

    private static final int BAUD_RATE = 57600;
    private static final int DATA_BITS = 8;
    private static final int STOP_BITS = 1;
    private static final int PARITY = 0;

    private final SerialPort serialPort = new SerialPort("COM3");
    private boolean runLoop;

    // These hold the last values sent to the Arduino. New values are only sent when they differ from
    // these old values.
    private Color lastCaseColor = null;
    private Color lastLcdColor = null;
    private final String[] lastLcdText = new String[Data.LCD_HEIGHT];
    private long lastCaseColorUpdateTime;
    private long lastLcdColorUpdateTime;
    private long lastLcdTextUpdateTime;

    private enum PacketTag {
        CASE_COLOR('c'), LCD_COLOR('l'), LCD_TEXT('t');

        private final char tag;

        PacketTag(char tag) {
            this.tag = tag;
        }
    }

    @Override
    public void start() {
        runLoop = true;
        super.start();
    }

    public void terminate() {
        runLoop = false;
    }

    @Override
    public void run() {
        while (runLoop) {
            // If the port isn't open, try to open it. Otherwise, send data.
            if (!serialPort.isOpened()) {
                try {
                    serialPort.openPort(); // Open the port because it isn't already
                    serialPort.setParams(BAUD_RATE, DATA_BITS, STOP_BITS, PARITY);
                } catch (SerialPortException e) {
                    System.err.printf("Error opening serial port. Will try again in %d ms.\n",
                                      STARTUP_TIME);
                }

                Funcs.pause(STARTUP_TIME); // Pause to let the serial port set up
            } else {
                final Data data = CaseControl.getData(); // The data to be written

                // Send all necessary data
                try {
                    writeCaseColor(data); // Write case color
                    writeLcdColor(data); // Write LCD color
                    writeText(data); // Write LCD text
                } catch (SerialPortException e) {
                    System.err.println("Error sending data over serial port.");
                    e.printStackTrace();
                }

                Funcs.pause(LOOP_TIME); // Pause for a bit
            }
        }

        // Close the port
        try {
            serialPort.closePort();
        } catch (SerialPortException e) {
            System.err.println("Error closing serial port.");
        }
    }

    /**
     * Writes the current case color to the serial port, IF the color has changed since it was last
     * written.
     *
     * @param data the data containing the current case color
     */
    private void writeCaseColor(Data data) throws SerialPortException {
        // If the case color changed, update it.
        if (lastCaseColor == null || !data.caseColor.equals(lastCaseColor)
            || timeToUpdate(lastCaseColorUpdateTime)) {
            writeColor(PacketTag.CASE_COLOR.tag, data.caseColor);
            lastCaseColor = data.caseColor;
            lastCaseColorUpdateTime = System.currentTimeMillis();
        }
    }

    /**
     * Writes the current LCD color to the serial port, IF the color has changed since it was last
     * written.
     *
     * @param data the data containing the current LCD color
     */
    private void writeLcdColor(Data data) throws SerialPortException {
        // If the case color changed, update it.
        if (lastLcdColor == null || !data.lcdColor.equals(lastLcdColor)
            || timeToUpdate(lastLcdColorUpdateTime)) {
            writeColor(PacketTag.LCD_COLOR.tag, data.lcdColor);
            lastLcdColor = data.lcdColor;
            lastLcdColorUpdateTime = System.currentTimeMillis();
        }
    }

    /**
     * Writes the current LCD text to the serial port, IF the text has changed since it was last
     * written.
     *
     * @param data the data containing the current LCD text
     */
    private void writeText(Data data) throws SerialPortException {
        if (!Arrays.equals(lastLcdText, data.lcdText) || timeToUpdate(lastLcdTextUpdateTime)) {
            serialPort
                .writeByte((byte) PacketTag.LCD_TEXT.tag); // Tell the Arduino words are coming

            // For each line in the text...
            for (String line : data.lcdText) {
                // If the line is too long for the LCD, chop it down.
                // If it's too short, pad it with spaces
                if (line.length() > Data.LCD_WIDTH) {
                    line = line.substring(0, Data.LCD_WIDTH);
                } else if (line.length() < Data.LCD_WIDTH) {
                    line = Funcs.padRight(line, Data.LCD_WIDTH);
                }
                writeStringToSerial(line); // Write the line
            }
            System.arraycopy(data.lcdText, 0, lastLcdText, 0, data.lcdText.length);
            lastLcdTextUpdateTime = System.currentTimeMillis();
        }
    }

    private void writeColor(char tag, Color color) throws SerialPortException {
        serialPort.writeBytes(new byte[]{
            (byte) tag, (byte) color.getRed(), (byte) color.getGreen(), (byte) color.getBlue()});
    }

    /**
     * Write the given string to the serial port. {@link SerialPort#writeString} wasn't working (but
     * only in IntelliJ) so I wrote this.
     *
     * I guess this is as good a place as any to describe the bug (so I don't run into it again):
     *
     * Under windows-1232 encoding, it works fine because it encodes characters into bytes exactly
     * according to the literal codes they're defined with, i.e. "\u00ff" will be decoded into 255
     * (or more accurately, 0b11111111, which will print as -1 for a signed byte). BUT, under UTF-8,
     * any character with a code 128+ will be encoded as 2+ bytes, so when a string containing that
     * character gets decoded, that character will be represented by multiple bytes in the
     * array/buffer/etc. {@link SerialPort#writeString} uses {@link String#getBytes} and treats each
     * byte in the array as one character (why wouldn't it). Unfortunately, for any character with
     * code 128+ (not typically relevant because ASCII only goes to 127), it will start screwing up
     * and everything will get offset by one byte (or more). I could make {@link
     * SerialPort#writeString} work by forcing the default encoding to windows-1232, but I'm not
     * sure how portable that is (will Linux like that?) and as far as I can tell, the only way to
     * do that is with a VM flag (-Dfile.encoding=windows-1232) when the program starts, and having
     * to remember to set up a VM flag is dumb. If you're future me and you're reading this, you're
     * welcome. If you're anyone else, why the hell are you reading this?
     *
     * @param s the string to be written
     */
    private void writeStringToSerial(String s) throws SerialPortException {
        for (char c : s.toCharArray()) {
            serialPort.writeByte((byte) c);
        }
    }

    /**
     * Is it time to update the Arduino again?
     *
     * @param lastUpdateTime the last time the relevant information was updated
     * @return true if it's been more than {@link #PING_FREQUENCY} ms since the last update
     */
    private boolean timeToUpdate(long lastUpdateTime) {
        return System.currentTimeMillis() - lastUpdateTime >= PING_FREQUENCY;
    }
}
