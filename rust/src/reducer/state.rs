use serde::{Deserialize, Serialize};

/// Current state of all hardware resources. This is read-write for both the
/// reducer and the hardware interface. The reducer writes LED/LCD state, and
/// the hardware writes keepalive state. We need to be careful about not
/// deadlocking on this.
#[derive(Debug, Default)]
pub struct HardwareState {
    keepalive: bool,
    led_color: RgbColor,
    /// LCD state is stored as an imperative queue instead of declarative
    /// state. This frontloads logic into the reducer, and makes it easier
    /// to do event-based logic like "turn off the LCD on shutdown".
    lcd_command_queue: Vec<u8>,
}

/// 32-bit Red-Green-Blue color
#[derive(
    Copy, Clone, Debug, Default, Eq, PartialEq, Serialize, Deserialize,
)]
#[serde(from = "u32", into = "u32")]

pub struct RgbColor {
    pub red: u8,
    pub green: u8,
    pub blue: u8,
}

// This is lossy, since we throw away the first 8 bytes. Hope it wasn't RGBA!
impl From<u32> for RgbColor {
    fn from(value: u32) -> Self {
        // Casting will truncate the 24 most significant bits
        let red = (value >> 16) as u8;
        let green = (value >> 8) as u8;
        let blue = value as u8;
        Self { red, green, blue }
    }
}

impl From<RgbColor> for u32 {
    fn from(color: RgbColor) -> Self {
        ((color.red as u32) << 16)
            | ((color.green as u32) << 8)
            | color.blue as u32
    }
}
