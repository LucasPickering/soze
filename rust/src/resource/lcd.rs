use crate::{
    resource::Resource,
    state::{common::Color, hardware, user},
};
use anyhow::{anyhow, bail};
use chrono::Local;
use log::{debug, trace};
use std::io::Write;

/// Width of the LCD, in characters
const LCD_WIDTH: usize = 20;
/// Height of the LCD in lines
const LCD_HEIGHT: usize = 4;

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

    fn on_start(
        &mut self,
        hardware_state: &mut Self::HardwareState,
    ) -> anyhow::Result<()> {
        let mut lcd: Lcd = hardware_state.into();
        lcd.command(LcdCommand::Clear); // Reset text state
        lcd.command(LcdCommand::BacklightOn);

        // Generally this init only needs to be done once ever, but it's safer
        // to do it on every startup
        lcd.command(LcdCommand::SetSize {
            width: LCD_WIDTH as u8,
            height: LCD_HEIGHT as u8,
        });
        lcd.command(LcdCommand::SetContrast { contrast: 255 });
        lcd.command(LcdCommand::SetBrightness { brightness: 255 });
        for &character in CustomCharacter::ALL {
            lcd.command(LcdCommand::SaveCustomCharacter { bank: 0, character });
        }
        lcd.command(LcdCommand::LoadCharacterBank { bank: 0 });
        Ok(())
    }

    fn on_tick(
        &mut self,
        user_state: &Self::UserState,
        hardware_state: &mut Self::HardwareState,
    ) -> anyhow::Result<()> {
        let mut lcd: Lcd = hardware_state.into();
        match user_state.mode {
            user::LcdMode::Off => {
                lcd.command(LcdCommand::BacklightOff);
                lcd.command(LcdCommand::Clear);
            }
            user::LcdMode::Clock => {
                self.set_color(&mut lcd, user_state.color);
                self.set_text(&mut lcd, get_clock_text()?);
            }
        }
        Ok(())
    }
}

impl LcdResource {
    /// Set background color. Does nothing if the color hasn't changed.
    fn set_color(&mut self, lcd: &mut Lcd, color: Color) {
        if self.color != color {
            self.color = color;
            lcd.command(LcdCommand::SetColor { color });
        }
    }

    /// Set LCD text. This will diff against current text and only send what's
    /// changed. The LCD is slow to update, so without diffing it will never
    /// settle. Input text is assumed to be ASCII, and have exactly [LCD_HEIGHT]
    /// lines.
    fn set_text(&mut self, lcd: &mut Lcd, text: LcdText) {
        debug!("Setting LCD text to {text:x?}");

        // A list of groups that need their text updated. Each group will end
        // either at a non-diff byte, or end of line
        let mut diff_groups: Vec<TextGroup> = Vec::new();
        let mut current_diff_group: Option<TextGroup> = None;
        // Helper to terminate a group. This can't capture current_diff_group,
        // because we need &mut to it below
        let mut finish_group = |diff_group: &mut Option<TextGroup>| {
            // Move the current group out of the option, if present
            if let Some(diff_group) = diff_group.take() {
                diff_groups.push(diff_group);
            }
        };

        // Figure out what's changed. We're going to make a very bold assumption
        // that the input text is ASCII. If not, shit's fucked. Top-left to
        // bottom-right, line by line.
        for y in 0..LCD_HEIGHT {
            for x in 0..LCD_WIDTH {
                let old_byte = self.text.get(x, y);
                let new_byte = self.text.get(x, y);

                // Save the new byte, then check if it's a diff
                self.text.set(x, y, new_byte);
                if old_byte == new_byte {
                    finish_group(&mut current_diff_group);
                } else {
                    match &mut current_diff_group {
                        // Start a new diff group
                        None => current_diff_group = Some(TextGroup::new(x, y)),
                        // Extend the current group
                        Some(diff_group) => {
                            diff_group.extend();
                        }
                    }
                }
            }

            // Always finish a group at the end of a line
            finish_group(&mut current_diff_group);
        }

        // Update the diffed sections
        for group in diff_groups {
            // LCD positions are 1-indexed!
            lcd.write_at(
                group.x as u8 + 1,
                group.y as u8 + 1,
                self.text.get_slice(&group),
            )
        }
    }
}

/// Wrapper for managing LCD state that makes it a bit more ergonomic to send
/// messages over the queue
struct Lcd<'a> {
    message_queue: &'a mut Vec<u8>,
}

impl<'a> Lcd<'a> {
    /// Convert a command to bytes and put it on the queue
    fn command(&mut self, command: LcdCommand) {
        trace!("Sending LCD command: {command:x?}");
        self.message_queue.extend(command.into_bytes())
    }

    /// Move the cursor to the given position, then write some text
    fn write_at(&mut self, x: u8, y: u8, text: &[u8]) {
        self.command(LcdCommand::CursorPos { x, y });
        // Non-command bytes are interpreted as text
        // https://learn.adafruit.com/usb-plus-serial-backpack/sending-text
        self.message_queue.extend(text);
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
    lines: [[u8; LCD_WIDTH]; LCD_HEIGHT],
}

impl LcdText {
    fn get(&self, x: usize, y: usize) -> u8 {
        self.lines[y][x]
    }

    fn set(&mut self, x: usize, y: usize, value: u8) {
        self.lines[y][x] = value;
    }

    /// Get a slice into a single line in the text. This assumes the
    /// position/length are valid!
    fn get_slice(&self, group: &TextGroup) -> &[u8] {
        &self.lines[group.y][group.x..group.x + group.length]
    }
}

impl Default for LcdText {
    fn default() -> Self {
        Self {
            // Default to whitespace
            lines: [[b' '; LCD_WIDTH]; LCD_HEIGHT],
        }
    }
}

/// Non-text commands for the LCD. There are more command types than this, but
/// we don't use them. Copy them in as needed.
/// https://learn.adafruit.com/usb-plus-serial-backpack/command-reference
#[derive(Debug)]
enum LcdCommand {
    Clear,
    BacklightOn,
    BacklightOff,
    SetSize {
        width: u8,
        height: u8,
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
    /// Move the cursor to start editing at this position. Positions are
    /// 1-based, not 0-based.
    CursorPos {
        x: u8,
        y: u8,
    },
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

impl LcdCommand {
    const COMMAND_BYTE: u8 = 0xFE;

    fn into_bytes(self) -> Vec<u8> {
        // Every command status with a sentinel byte, followed by a tag byte
        let mut buffer = vec![Self::COMMAND_BYTE, self.tag()];

        // These writes are all infallible because they're into a buffer
        match self {
            Self::Clear => {}
            // Second param is the number of minutes to stay on, but it doesn't
            // actually get used, so we don't parameterize it
            Self::BacklightOn => buffer.write_all(&[0]).unwrap(),
            Self::BacklightOff => {}
            Self::SetSize { width, height } => {
                buffer.write_all(&[width, height]).unwrap()
            }
            Self::SetBrightness { brightness } => {
                buffer.write_all(&[brightness]).unwrap()
            }
            Self::SetContrast { contrast } => {
                buffer.write_all(&[contrast]).unwrap()
            }
            Self::SetColor { color } => {
                buffer.write_all(&color.to_bytes()).unwrap()
            }
            Self::CursorPos { x, y } => buffer.write_all(&[x, y]).unwrap(),
            Self::SaveCustomCharacter { bank, character } => {
                buffer.write_all(&[0xC1, bank, character.tag()]).unwrap();
                buffer.write_all(&character.pixels()).unwrap();
            }
            Self::LoadCharacterBank { bank } => {
                buffer.write_all(&[bank]).unwrap()
            }
        }

        buffer
    }

    /// Get the one-byte indentifier for a command type
    fn tag(&self) -> u8 {
        match self {
            Self::Clear => 0x58,
            Self::BacklightOn => 0x42,
            Self::BacklightOff => 0x46,
            Self::SetSize { .. } => 0xD1,
            Self::SetBrightness { .. } => 0x98,
            Self::SetContrast { .. } => 0x91,
            Self::SetColor { .. } => 0xD0,
            Self::CursorPos { .. } => 0x47,
            Self::SaveCustomCharacter { .. } => 0xC1,
            Self::LoadCharacterBank { .. } => 0xC0,
        }
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

/// A group of contiguous characters in a text block. Used to select blocks of
/// text for diff-only updating. This intentionally does *not* implement Copy,
/// to prevent logic bugs when mutating collections/options of this.
///
/// Groups *cannot* span multiple lines.
#[derive(Debug)]
struct TextGroup {
    x: usize,
    y: usize,
    length: usize,
}

impl TextGroup {
    fn new(x: usize, y: usize) -> Self {
        Self { x, y, length: 1 }
    }

    fn extend(&mut self) {
        self.length += 1;
    }
}

/// Format the current date+time as LCD text
fn get_clock_text() -> anyhow::Result<LcdText> {
    let now = Local::now();
    let mut text = LcdText::default();

    // First line is date and seconds. Month is abbreviated to prevent overflow
    let date = now.format("%A, %b %-d");
    let seconds = now.format("%S");
    // This should always be 20 chars
    text.lines[0] = format!("{date:<18}{seconds}")
        .into_bytes()
        .try_into()
        .map_err(|bytes| {
            anyhow!(
                "First clock line has incorrect length. \
                Expected {LCD_WIDTH} bytes, received {bytes:?}",
            )
        })?;

    // Next three lines are the time, in jumbo text
    let time = now.format("%-I:%M").to_string();
    // This unwrap is safe because the length of lines is fixed
    write_jumbo_text((&mut text.lines[1..4]).try_into().unwrap(), &time)?;

    Ok(text)
}

/// Render a string as jumbo text. Jumbo characters are 3 lines tall, so we
/// need a 3-line slice.
fn write_jumbo_text(
    line_buffer: &mut [[u8; LCD_WIDTH]; 3],
    text: &str,
) -> anyhow::Result<()> {
    let x = 0;
    for c in text.as_bytes() {
        // For each line, copy the bytes into our text array
        let jumbo_bytes = get_jumbo_character(*c)?;
        for y in 0..3 {
            let jumbo_bytes_line = jumbo_bytes[y];
            line_buffer[y][x..x + jumbo_bytes_line.len()]
                .copy_from_slice(jumbo_bytes_line);
        }
    }
    Ok(())
}

/// Get the bytes for a single jumbo character. Each character is exactly 3
/// bytes tall, but they have varying widths.
fn get_jumbo_character(character: u8) -> anyhow::Result<[&'static [u8]; 3]> {
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
    let bytes: [&[u8]; 3] = match character {
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
            bail!("Cannot convert character `{character}` to jumbo text");
        }
    };
    Ok(bytes)
}
