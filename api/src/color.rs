use lazy_static::lazy_static;
use regex::Regex;
use serde::{de::Visitor, Deserialize, Deserializer, Serialize, Serializer};
use std::fmt;

/// A 24-bit RGB color. For easy interaction with the UI, these a color gets
/// serialized as an HTML hex code (#rrggbb). This includes when it's serialized
/// into Redis to be passed to the reducer.
#[derive(Copy, Clone, Debug, Default)]
pub struct Color {
    pub red: u8,
    pub green: u8,
    pub blue: u8,
}

impl Color {
    /// Convert to an HTML string
    pub fn to_html(self) -> String {
        format!("#{:02x}{:02x}{:02x}", self.red, self.green, self.blue)
    }
}

// Serialization - pack the color as a 32-bit int (top 8 bits are dead space)
impl Serialize for Color {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_str(&self.to_html())
    }
}

impl<'de> Deserialize<'de> for Color {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        deserializer.deserialize_str(ColorHtmlVisitor)
    }
}

// Logic below is to deserialize HTML strings into colors
lazy_static! {
    static ref HTML_COLOR_REGEX: Regex =
        Regex::new("^#([0-9a-fA-F]{6})$").unwrap();
}

struct ColorHtmlVisitor;

impl<'de> Visitor<'de> for ColorHtmlVisitor {
    type Value = Color;

    fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
        formatter.write_str("a string of the format `#rrggbb`")
    }

    fn visit_str<E>(self, value: &str) -> Result<Self::Value, E>
    where
        E: serde::de::Error,
    {
        let captures = HTML_COLOR_REGEX
            .captures(value)
            .ok_or_else(|| serde::de::Error::custom("invalid color format"))?;
        // Parse string as a hex integer
        let s = captures.get(1).unwrap().as_str();
        let color_int: u32 =
            u32::from_str_radix(s, 16).map_err(serde::de::Error::custom)?;

        // Convert 24 bit color to 3 separate bytes
        let red = ((color_int >> 16) & 0xff) as u8;
        let green = ((color_int >> 8) & 0xff) as u8;
        let blue = (color_int & 0xff) as u8;
        Ok(Color { red, green, blue })
    }
}
