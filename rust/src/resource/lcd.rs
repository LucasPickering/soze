use crate::{
    resource::Resource,
    state::{common::Color, hardware, user},
};
use chrono::Local;
use log::error;
use std::{collections::VecDeque, io::Write};

/// Width of the LCD, in characters
const LCD_WIDTH: u8 = 20;
/// Height of the LCD in lines
const LCD_HEIGHT: u8 = 4;

#[derive(Default)]
pub struct LcdResource {
    color: Color,
    text: LcdText,
}

impl Resource for LcdResource {
    type UserState = user::LcdState;
    type HardwareState = hardware::LcdState;

    fn get_user_state(
        global_state: &user::AllResourceState,
    ) -> &user::ResourceState<Self::UserState> {
        &global_state.lcd
    }

    fn get_user_state_mut(
        global_state: &mut user::AllResourceState,
    ) -> &mut user::ResourceState<Self::UserState> {
        &mut global_state.lcd
    }

    fn on_start(&mut self, hardware_state: &mut Self::HardwareState) {
        let mut lcd: Lcd = hardware_state.into();
        lcd.send(Message::BacklightOn);
        // Generally this init only needs to be done once ever, but it's safer
        // to do it on every startup
        lcd.send(Message::SetSize {
            width: LCD_WIDTH,
            height: LCD_HEIGHT,
        });
        lcd.send(Message::SetContrast { contrast: 255 });
        lcd.send(Message::SetBrightness { brightness: 255 });
        for &character in CustomCharacter::ALL {
            lcd.send(Message::SaveCustomCharacter { bank: 0, character });
        }
    }

    fn on_tick(
        &mut self,
        user_state: &Self::UserState,
        hardware_state: &mut Self::HardwareState,
    ) {
        let mut lcd: Lcd = hardware_state.into();
        match user_state.mode {
            user::LcdMode::Off => {
                lcd.send(Message::BacklightOff);
                lcd.send(Message::Clear);
            }
            user::LcdMode::Clock => {
                self.set_color(&mut lcd, user_state.color);
                self.set_text(&mut lcd, get_clock_text());
            }
        }
    }
}

impl LcdResource {
    /// Set background color. Does nothing if the color hasn't changed.
    fn set_color(&mut self, lcd: &mut Lcd, color: Color) {
        if self.color != color {
            self.color = color;
            lcd.send(Message::SetColor { color });
        }
    }

    /// Set LCD text. This will diff against current text and only send what's
    /// changed. The LCD is slow to update, so without diffing it will never
    /// settle. Input text is assumed to be ASCII, and have exactly [LCD_HEIGHT]
    /// lines.
    ///
    /// We accept an array of strings here, instead of fixed-length char
    /// buffers, to make it a bit more ergonomic to build up text content.
    fn set_text(&mut self, lcd: &mut Lcd, text: [String; LCD_HEIGHT as usize]) {
        fn pos(x: u8, y: u8) -> usize {
            (y * LCD_WIDTH + x) as usize
        }

        // A list of groups that need their text updated as (x, y, length)
        let mut diff_groups: Vec<(u8, u8, usize)> = Vec::new();

        // Figure out what's changed. We're going to make a very bold assumption
        // that the input text is ASCII. If not, shit's fucked.
        let mut current_diff_group: Option<(u8, u8, usize)> = None;
        // Top-left to bottom-right, line by line
        for y in 0..LCD_HEIGHT {
            let line = text[y as usize].as_bytes();
            for x in 0..LCD_WIDTH {
                // Old text is fixed size so this index is safe
                let old_byte = self.text.bytes[pos(x, y)];
                // Line is variable size. Default to blank
                let new_byte = line.get(x as usize).copied().unwrap_or(b' ');
                match (current_diff_group, old_byte == new_byte) {
                    // Differing part has ended
                    (Some(diff_group), true) => {
                        diff_groups.push(diff_group);
                        current_diff_group = None;
                    }
                    // Extend the current group
                    (Some(mut diff_group), false) => {
                        diff_group.2 += 1;
                    }
                    // Nothing to do here
                    (None, true) => {}
                    // Start a new diff group
                    (None, false) => current_diff_group = Some((x, y, 1)),
                }
            }
        }

        // Update the diffed sections
        for (x, y, length) in diff_groups {
            let start = pos(x, y);
            lcd.write_at(x, y, &self.text.bytes[start..start + length])
        }
    }
}

/// Wrapper for managing LCD state that makes it a bit more ergonomic to send
/// messages over the queue
struct Lcd<'a> {
    message_queue: &'a mut VecDeque<u8>,
}

impl<'a> Lcd<'a> {
    /// Convert a message to bytes and put it on the queue
    fn send(&mut self, message: Message) {
        self.message_queue.extend(message.into_bytes())
    }

    /// Move the cursor to the given position, then write some text
    fn write_at(&mut self, x: u8, y: u8, text: &[u8]) {
        self.send(Message::CursorPos { x, y });
        self.send(Message::Text {
            bytes: text.to_owned(),
        })
    }
}

impl<'a> From<&'a mut hardware::LcdState> for Lcd<'a> {
    fn from(hardware_state: &'a mut hardware::LcdState) -> Self {
        Self {
            message_queue: &mut hardware_state.message_queue,
        }
    }
}

/// Text on the LCD. Use bytes instead of str/char because those allow unicode,
/// which we don't support. Every character is one byte in this world. The LCD
/// has autowrap enabled by default, so we can just shit out a stream of bytes
/// and it will figure it out.
#[derive(Copy, Clone, Debug)]
struct LcdText {
    bytes: [u8; (LCD_WIDTH * LCD_HEIGHT) as usize],
}

impl Default for LcdText {
    fn default() -> Self {
        Self {
            // Default to whitespace
            bytes: [b' '; (LCD_WIDTH * LCD_HEIGHT) as usize],
        }
    }
}

/// Serial message for the LCD controller
/// https://learn.adafruit.com/usb-plus-serial-backpack/command-reference
#[derive(Clone, Debug)]
enum Message {
    /// Write an arbitrary number of bytes at the current position
    /// https://learn.adafruit.com/usb-plus-serial-backpack/sending-text
    Text {
        bytes: Vec<u8>,
    },
    Clear,
    BacklightOn,
    BacklightOff,
    SetSize {
        width: u8,
        height: u8,
    },
    SplashText {
        text: LcdText,
    },
    SetBrightness {
        brightness: u8,
    },
    SetContrast {
        contrast: u8,
    },
    SetColor {
        color: Color,
    },
    AutoscrollOn,
    AutoscrollOff,
    UnderlineCursorOn,
    UnderlineCursorOff,
    BlockCursorOn,
    BlockCursorOff,
    CursorHome,
    CursorPos {
        x: u8,
        y: u8,
    },
    CursorForward,
    CursorBack,
    CreateCharacter,
    /// Initialize a custom character, to be used later. The character will be
    /// accessed by its tag (from [CustomCharacter::tag])
    SaveCustomCharacter {
        bank: u8,
        character: CustomCharacter,
    },
    LoadCharacterBank {
        bank: u8,
    },
}

impl Message {
    const COMMAND_BYTE: u8 = 0xFE;

    pub fn into_bytes(self) -> Vec<u8> {
        let mut buffer = vec![Self::COMMAND_BYTE];
        // These writes are all infallible because they're into a buffer
        match self {
            // Return the text byte buffer immediately, so we don't include the
            // command byte from above
            Self::Text { bytes } => return bytes,
            Self::Clear => buffer.write_all(&[0x58]),
            // Second param is the number of minutes to stay on, but it doesn't
            // actually get used, so we don't parameterize it
            Self::BacklightOn => buffer.write_all(&[0x42, 0]),
            Self::BacklightOff => buffer.write_all(&[0x46]),
            Self::SetSize { width, height } => {
                buffer.write_all(&[0xD1, width, height])
            }
            Self::SplashText { text } => {
                buffer.write_all(&[0x40]).unwrap();
                buffer.write_all(&text.bytes)
            }
            Self::SetBrightness { brightness } => {
                buffer.write_all(&[0x98, brightness])
            }
            Self::SetContrast { contrast } => {
                buffer.write_all(&[0x91, contrast])
            }
            Self::SetColor { color } => {
                buffer.write_all(&[0xD0]).unwrap();
                buffer.write_all(&color.to_bytes())
            }
            Self::AutoscrollOn => buffer.write_all(&[0x51]),
            Self::AutoscrollOff => buffer.write_all(&[0x52]),
            Self::UnderlineCursorOn => buffer.write_all(&[0x4A]),
            Self::UnderlineCursorOff => buffer.write_all(&[0x4B]),
            Self::BlockCursorOn => buffer.write_all(&[0x53]),
            Self::BlockCursorOff => buffer.write_all(&[0x54]),
            Self::CursorHome => buffer.write_all(&[0x48]),
            Self::CursorPos { x, y } => buffer.write_all(&[0x47, x, y]),
            Self::CursorForward => buffer.write_all(&[0x4D]),
            Self::CursorBack => buffer.write_all(&[0x4C]),
            Self::CreateCharacter => buffer.write_all(&[0x4E]),
            Self::SaveCustomCharacter { bank, character } => {
                buffer.write_all(&[0xC1, bank, character.tag()]).unwrap();
                buffer.write_all(&character.pixels())
            }
            Self::LoadCharacterBank { bank } => buffer.write_all(&[0xC0, bank]),
        }
        .unwrap();
        buffer
    }
}

/// Custom characters that are used to create jumbo (multi-line) characters.
/// Each of these is defined as a 5x8 grid of pixels.
#[derive(Copy, Clone, Debug)]
enum CustomCharacter {
    HalfBottomRight,
    HalfBottomLeft,
    Bottom,
    FullBottomRight,
    FullBottomLeft,
}

impl CustomCharacter {
    const ALL: &'static [Self] = &[
        Self::HalfBottomRight,
        Self::HalfBottomLeft,
        Self::Bottom,
        Self::FullBottomLeft,
        Self::FullBottomRight,
    ];

    /// The byte representing this character when writing text. Also, the index
    /// of the character in the character bank
    const fn tag(self) -> u8 {
        match self {
            Self::HalfBottomRight => 0x00,
            Self::HalfBottomLeft => 0x01,
            Self::Bottom => 0x02,
            Self::FullBottomRight => 0x03,
            Self::FullBottomLeft => 0x04,
        }
    }

    /// Get the pixel grid that defines this character. Each character is 8
    /// lines of 5 pixels each, where each pixel can be on or off. These need
    /// to be loaded into the LCD at boot.
    fn pixels(self) -> [u8; 8] {
        match self {
            Self::HalfBottomRight => [
                0b00000, 0b00000, 0b00000, 0b00000, 0b00011, 0b01111, 0b01111,
                0b11111,
            ],
            Self::HalfBottomLeft => [
                0b00000, 0b00000, 0b00000, 0b00000, 0b11000, 0b11110, 0b11110,
                0b11111,
            ],
            Self::Bottom => [
                0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111, 0b11111,
                0b11111,
            ],
            Self::FullBottomRight => [
                0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b01111, 0b01111,
                0b00011,
            ],
            Self::FullBottomLeft => [
                0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11110, 0b11110,
                0b11000,
            ],
        }
    }
}

/// Format the current date+time as LCD text
fn get_clock_text() -> [String; LCD_HEIGHT as usize] {
    let now = Local::now();

    // First line is date and seconds. Month is abbreviated to prevent overflow
    let date = now.format("%A, %b %-d");
    let seconds = now.format("%S");
    let mut lines = [
        format!("{date:<18}{seconds}"),
        String::new(),
        String::new(),
        String::new(),
    ];

    // Next three lines are the time, in jumbo text
    let time = now.format("%-I:%M").to_string();
    // This unwrap is safe because the length of lines is fixed
    write_jumbo_text((&mut lines[1..4]).try_into().unwrap(), &time);

    lines
}

/// Render a string as jumbo text. Jumbo characters are 3 lines tall, so we
/// return 3 strings.
fn write_jumbo_text(line_buffer: &mut [String; 3], text: &str) {
    for c in text.as_bytes() {
        write_jumbo_character(line_buffer, *c);
    }
}

/// Write a single jumbo character to a line buffer. Each jumbo character spans
/// 3 lines, so this will write `n` bytes to each line, where `n > 1`.
fn write_jumbo_character(line_buffer: &mut [String; 3], character: u8) {
    // Convenient consts for building up jumbo characters
    const HBR: u8 = CustomCharacter::HalfBottomRight.tag();
    const HBL: u8 = CustomCharacter::HalfBottomLeft.tag();
    const BOT: u8 = CustomCharacter::Bottom.tag();
    const FBR: u8 = CustomCharacter::FullBottomRight.tag();
    const FBL: u8 = CustomCharacter::FullBottomLeft.tag();
    const FUL: u8 = 0xff; // Solid block (built-in to the LCD)
    const EMT: u8 = b' '; // Empty

    // We know how many lines we're modifying, but we *don't* know how many
    // chars per line we're writing, so those have to be strs
    let to_write: [&[u8]; 3] = match character {
        b'0' => [&[HBR, BOT, HBL], &[FUL, EMT, FUL], &[FBR, BOT, FBL]],
        b'1' => [&[BOT, HBL, EMT], &[EMT, FUL, EMT], &[BOT, FUL, BOT]],
        b'2' => [&[HBR, BOT, HBL], &[HBR, BOT, FBL], &[FBR, BOT, BOT]],
        b'3' => [&[HBR, BOT, HBL], &[EMT, BOT, FUL], &[BOT, BOT, FBL]],
        b'4' => [&[BOT, EMT, BOT], &[FBR, BOT, FUL], &[EMT, EMT, FUL]],
        b'5' => [&[BOT, BOT, BOT], &[FUL, BOT, HBL], &[BOT, BOT, FBL]],
        b'6' => [&[HBR, BOT, HBL], &[FUL, BOT, HBL], &[FBR, BOT, FBL]],
        b'7' => [&[BOT, BOT, BOT], &[EMT, HBR, FBL], &[EMT, FUL, EMT]],
        b'8' => [&[HBR, BOT, HBL], &[FUL, BOT, FUL], &[FBR, BOT, FBL]],
        b'9' => [&[HBR, BOT, HBL], &[FBR, BOT, FUL], &[EMT, EMT, FUL]],
        b' ' => [&[EMT, EMT, EMT], &[EMT, EMT, EMT], &[EMT, EMT, EMT]],
        b':' => [&[FUL], &[EMT], &[FUL]],
        _ => {
            error!("Cannot convert character `{character}` to jumbo text");
            return;
        }
    };

    // Write all the new characters to each line
    for i in 0..3 {
        let line = &mut line_buffer[i];
        // Pre-pad each character with a single space, for better readabilty
        line.push(' ');
        // Convert from u8 to char for each character
        line.extend(to_write[i].iter().copied().map(char::from));
    }
}
