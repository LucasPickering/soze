use crate::color::HtmlColor;
use log::info;
use serde::{Deserialize, Serialize};
use std::{collections::HashMap, io, path::PathBuf};
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
