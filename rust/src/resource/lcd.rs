use crate::{
    resource::Resource,
    state::{common::Color, hardware, user},
};
use std::{collections::VecDeque, io::Write};

/// Width of the LCD, in characters
pub const LCD_WIDTH: u8 = 20;
/// Height of the LCD in lines
pub const LCD_HEIGHT: u8 = 4;

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
        lcd.on();
        lcd.set_size(LCD_WIDTH, LCD_HEIGHT);
        lcd.set_contrast(255);
        lcd.set_brightness(255);
    }

    fn on_tick(
        &mut self,
        user_state: &Self::UserState,
        hardware_state: &mut Self::HardwareState,
    ) {
        let mut lcd: Lcd = hardware_state.into();
        match user_state.mode {
            user::LcdMode::Off => {
                lcd.off();
                lcd.clear();
            }
            user::LcdMode::Clock => {
                self.set_color(&mut lcd, user_state.color);
                self.set_text(&mut lcd, vec!["TODO".to_owned()]);
            }
        }
    }
}

impl LcdResource {
    /// Set background color. Does nothing if the color hasn't changed.
    fn set_color(&mut self, lcd: &mut Lcd, color: Color) {
        if self.color != color {
            self.color = color;
            lcd.set_color(color);
        }
    }

    /// Set LCD text. This will diff against current text and only send what's
    /// changed. The LCD is slow to update, so without diffing it will never
    /// settle. Input text is assumed to be ASCII, and have exactly [LCD_HEIGHT]
    /// lines.
    fn set_text(&mut self, lcd: &mut Lcd, text: Vec<String>) {
        fn pos(x: u8, y: u8) -> usize {
            (y * LCD_WIDTH + x) as usize
        }

        assert_eq!(
            text.len(),
            LCD_HEIGHT as usize,
            "text should have exactly {LCD_HEIGHT} lines"
        );

        // A list of groups that need their text updated as (x, y, length)
        let mut diff_groups: Vec<(u8, u8, usize)> = Vec::new();

        // Figure out what's changed. We're going to make a very bold assumption
        // that the input text is ASCII. If not, shit's fucked.
        let mut current_diff_group: Option<(u8, u8, usize)> = None;
        // Top-left to bottom-right, line by line
        for y in 0..LCD_HEIGHT {
            let line = text[y as usize].as_bytes();
            for x in 0..LCD_WIDTH {
                let old_byte = self.text.bytes[pos(x, y)];
                let new_byte = line[x as usize];
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
            lcd.set_cursor_pos(x, y);
            let start = pos(x, y);
            lcd.write_text(&self.text.bytes[start..start + length])
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
    fn send(&mut self, message: LcdMessage) {
        self.message_queue.extend(message.into_bytes())
    }

    /// Clear all text
    fn clear(&mut self) {
        self.send(LcdMessage::Clear)
    }

    /// Turn the backlight on
    fn on(&mut self) {
        self.send(LcdMessage::BacklightOn { minutes: 0 })
    }

    /// Turn the backlight off
    fn off(&mut self) {
        self.send(LcdMessage::BacklightOff)
    }

    /// Set LCD dimensions
    fn set_size(&mut self, width: u8, height: u8) {
        self.send(LcdMessage::SetSize { width, height })
    }

    /// Set backlight brighness
    fn set_brightness(&mut self, brightness: u8) {
        self.send(LcdMessage::SetBrightness { brightness })
    }
    /// Set backlight contrast
    fn set_contrast(&mut self, contrast: u8) {
        self.send(LcdMessage::SetContrast { contrast })
    }

    /// Set background color
    fn set_color(&mut self, color: Color) {
        self.send(LcdMessage::SetColor { color })
    }

    /// Set cursor to the (x,y) position
    fn set_cursor_pos(&mut self, x: u8, y: u8) {
        self.send(LcdMessage::CursorPos { x, y })
    }

    fn write_text(&mut self, bytes: &[u8]) {
        self.send(LcdMessage::Text {
            bytes: bytes.to_owned(),
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
enum LcdMessage {
    /// Write an arbitrary number of bytes at the current position
    /// https://learn.adafruit.com/usb-plus-serial-backpack/sending-text
    Text {
        bytes: Vec<u8>,
    },
    Clear,
    BacklightOn {
        /// This value doesn't actually get used
        minutes: u8,
    },
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

impl LcdMessage {
    const COMMAND_BYTE: u8 = 0xFE;

    pub fn into_bytes(self) -> Vec<u8> {
        let mut buffer = vec![Self::COMMAND_BYTE];
        // These writes are all infallible because they're into a buffer
        match self {
            // Return the text byte buffer immediately, so we don't include the
            // command byte from above
            Self::Text { bytes } => return bytes,
            Self::Clear => buffer.write_all(&[0x58]),
            Self::BacklightOn { minutes } => buffer.write_all(&[0x42, minutes]),
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

/// Custom characters that are used to create big (multi-line) characters.
/// Each of these is defined as a 5x8 grid of pixels.
#[derive(Copy, Clone, Debug)]
enum CustomCharacter {
    HalfBottomRight,
    HalfBottomLeft,
    Bottom,
    FullBottomRight,
    FullBottomLeft,
    // TODO do these belong here?
    Full,
    Empty,
}

impl CustomCharacter {
    /// The byte representing this character when writing text. Also, the index
    /// of the character in the character bank
    fn tag(self) -> u8 {
        match self {
            Self::HalfBottomRight => 0x00,
            Self::HalfBottomLeft => 0x01,
            Self::Bottom => 0x02,
            Self::FullBottomRight => 0x03,
            Self::FullBottomLeft => 0x04,
            Self::Full => 0xff,
            Self::Empty => b' ',
        }
    }

    /// Get the pixel grid that defines this character. Each character is 8
    /// lines of 5 pixels each, where each pixel can be on or off.
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
            Self::Full => todo!(),
            Self::Empty => todo!(),
        }
    }
}
