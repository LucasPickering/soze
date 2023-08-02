use crate::api::error::ApiError;
use serde::{Deserialize, Serialize};
use std::{fmt::Display, str::FromStr};

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

/// 32-bit RGB color, but serialization/deserialization uses the HTML format of
/// "#rrggbb".
#[derive(
    Copy, Clone, Debug, Default, Eq, PartialEq, Serialize, Deserialize,
)]
#[serde(try_from = "String", into = "String")]

pub struct HtmlColor(pub RgbColor);

// This is lossy, since we throw away the first 8 bytes. Hope it wasn't RGBA!
impl FromStr for HtmlColor {
    type Err = ApiError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        if s.len() == 7 && s.starts_with('#') {
            let value = u32::from_str_radix(&s[1..], 16)?;
            Ok(Self(value.into()))
        } else {
            Err(ApiError::Validation {
                input: s.to_string(),
            })
        }
    }
}

impl Display for HtmlColor {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "#{:0>2x}{:0>2x}{:0>2x}",
            self.0.red, self.0.green, self.0.blue
        )
    }
}

// These impls are needed for serde
impl TryFrom<String> for HtmlColor {
    type Error = <HtmlColor as FromStr>::Err;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        value.parse()
    }
}
impl From<HtmlColor> for String {
    fn from(color: HtmlColor) -> Self {
        color.to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_color() {
        assert_eq!(
            "#000000".parse::<HtmlColor>().unwrap(),
            HtmlColor(0x000000.into())
        );
        assert_eq!(
            "#ff1234".parse::<HtmlColor>().unwrap(),
            HtmlColor(0xff1234.into())
        );
        assert_eq!(
            "#FFFFFF".parse::<HtmlColor>().unwrap(),
            HtmlColor(0xffffff.into())
        );

        assert!("#fffff".parse::<HtmlColor>().is_err()); // Too short
        assert!("#fffffff".parse::<HtmlColor>().is_err()); // Too long
        assert!("ffffff".parse::<HtmlColor>().is_err()); // No #
        assert!("@fffffg".parse::<HtmlColor>().is_err()); // Incorrect prefix
        assert!("#fffffg".parse::<HtmlColor>().is_err()); // bad char
    }

    #[test]
    fn test_display_color() {
        assert_eq!(HtmlColor(0x000000.into()).to_string().as_str(), "#000000");
        assert_eq!(HtmlColor(0xff00ff.into()).to_string().as_str(), "#ff00ff");
        assert_eq!(HtmlColor(0xffffff.into()).to_string().as_str(), "#ffffff");
    }
}
