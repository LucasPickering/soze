use crate::{api::error::ApiError, reducer::state::RgbColor};
use log::info;
use serde::{Deserialize, Serialize};
use std::{
    collections::HashMap, fmt::Display, io, path::PathBuf, str::FromStr,
};
use tokio::fs;

// TODO doc comments

const STATE_FILE: &str = "./soze_state.json";

/// User-managed state, i.e. what is exposed by the API and appears in the UI.
/// This is writable by the API, and read-only for the reducer.
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct UserState {
    pub led: Resource<LedState>,
    pub lcd: Resource<LcdState>,
}

impl UserState {
    /// Load state from a file if it exists, otherwise create default state and
    /// save that to the file
    pub async fn load() -> io::Result<Self> {
        info!("Reading user state from {STATE_FILE}");
        let path = PathBuf::from(STATE_FILE);
        let user_state = if path.exists() {
            let content = fs::read(STATE_FILE).await?;
            serde_json::from_slice(&content)?
        } else {
            info!("{STATE_FILE} missing, using default state");
            let user_state = Self::default();
            user_state.save().await?;
            user_state
        };
        info!("Initial user state: {user_state:?}");
        Ok(user_state)
    }

    pub async fn save(&self) -> io::Result<()> {
        info!("Saving user state to {STATE_FILE}");
        let content = serde_json::to_vec_pretty(self)?;
        fs::write(STATE_FILE, &content).await?;
        Ok(())
    }
}

/// All the states for a resource (LED or LCD), one per status. Right now this
/// is static since there's only two fields, but we can change it to a hashmap
/// if we add a bunch more statuses (unlikely).
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct Resource<T> {
    pub normal: T,
    pub sleep: T,
}

impl<T> Resource<T> {
    /// Get reference to state for a particular status
    pub fn get(&self, status: Status) -> &T {
        match status {
            Status::Normal => &self.normal,
            Status::Sleep => &self.sleep,
        }
    }

    /// Get mutable reference to state for a particular status
    pub fn get_mut(&mut self, status: Status) -> &mut T {
        match status {
            Status::Normal => &mut self.normal,
            Status::Sleep => &mut self.sleep,
        }
    }
}

#[derive(Copy, Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Status {
    Normal,
    Sleep,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct LedState {
    pub mode: LedMode,
    #[serde(rename = "static")]
    pub static_: LedStaticState,
    pub fade: LedFadeState,
}

#[derive(Copy, Clone, Debug, Default, Serialize, Deserialize)]
pub struct LedStaticState {
    pub color: HtmlColor,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct LedFadeState {
    pub colors: Vec<HtmlColor>,
    pub saved: HashMap<String, Vec<HtmlColor>>,
    // TODO validate this field
    pub fade_time: f32,
}

#[derive(Copy, Clone, Debug, Default, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LedMode {
    #[default]
    Off,
    Static,
    Fade,
}

#[derive(Copy, Clone, Debug, Default, Serialize, Deserialize)]
pub struct LcdState {
    pub mode: LcdMode,
    pub color: HtmlColor,
}

#[derive(Copy, Clone, Debug, Default, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LcdMode {
    #[default]
    Off,
    Clock,
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
