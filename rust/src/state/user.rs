//! User state, which is modified in the API and accessed read-only in the
//! reducer.

use crate::state::common::{Color, Status};
use log::{error, info};
use serde::{Deserialize, Serialize};
use std::{collections::HashMap, io, path::PathBuf, time::Duration};
use tokio::fs;

const STATE_FILE: &str = "./soze_state.json";

/// Top-level user-managed state, i.e. what is exposed by the API and appears in
/// the UI. This is writable by the API, and read-only for the reducer.
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct AllResourceState {
    pub led: ResourceState<LedState>,
    pub lcd: ResourceState<LcdState>,
}

impl AllResourceState {
    /// Load state from a file if it exists, otherwise create default state and
    /// save that to the file
    pub async fn load() -> io::Result<Self> {
        info!("Reading user state from {STATE_FILE}");
        let path = PathBuf::from(STATE_FILE);
        let user_state = if path.exists() {
            let content = fs::read(STATE_FILE).await?;
            serde_json::from_slice(&content).unwrap_or_else(|err| {
                error!(
                    "Error deserializing saved user state, using default: \
                    {err}"
                );
                Self::default()
            })
        } else {
            info!("{STATE_FILE} missing, using default state");
            Self::default()
        };
        // Write state back to disk, in case we had to fall back to default
        user_state.save().await?;

        info!("Initial user state: {user_state:?}");
        Ok(user_state)
    }

    /// Save this state to disk
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
pub struct ResourceState<T> {
    pub normal: T,
    pub sleep: T,
}

impl<T> ResourceState<T> {
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

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct LedState {
    pub mode: LedMode,
    #[serde(rename = "static")]
    pub static_: LedStaticState,
    pub fade: LedFadeState,
}

#[derive(Copy, Clone, Debug, Default, Serialize, Deserialize)]
pub struct LedStaticState {
    pub color: Color,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LedFadeState {
    pub colors: Vec<Color>,
    pub saved: HashMap<String, Vec<Color>>,
    /// (De)serializes as a float of seconds. Deserialization includes bounding
    /// validation.
    #[serde(with = "serde_fade_time")]
    pub fade_time: Duration,
}

impl Default for LedFadeState {
    fn default() -> Self {
        Self {
            colors: Vec::new(),
            saved: HashMap::new(),
            fade_time: Duration::from_secs(5),
        }
    }
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
    pub color: Color,
}

#[derive(Copy, Clone, Debug, Default, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LcdMode {
    #[default]
    Off,
    Clock,
}

/// Serialization/deserialization for fade_time field. Convert duration to a
/// float of seconds. Includes range-based validation.
mod serde_fade_time {
    use super::*;
    use serde::{
        de::{self, Unexpected, Visitor},
        Deserializer, Serializer,
    };

    pub fn serialize<S>(
        value: &Duration,
        serializer: S,
    ) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_f32(value.as_secs_f32())
    }

    pub fn deserialize<'de, D>(deserializer: D) -> Result<Duration, D::Error>
    where
        D: Deserializer<'de>,
    {
        const MIN: Duration = Duration::from_secs(1);
        const MAX: Duration = Duration::from_secs(30);
        struct FadeTimeVisitor;

        impl<'de> Visitor<'de> for FadeTimeVisitor {
            type Value = Duration;

            fn expecting(
                &self,
                f: &mut std::fmt::Formatter,
            ) -> std::fmt::Result {
                write!(
                    f,
                    "float between {} and {} seconds",
                    MIN.as_secs(),
                    MAX.as_secs()
                )
            }

            fn visit_f64<E: de::Error>(self, v: f64) -> Result<Duration, E> {
                let duration = Duration::from_secs_f64(v);
                if MIN <= duration && duration <= MAX {
                    Ok(duration)
                } else {
                    Err(E::invalid_value(
                        Unexpected::Float(v),
                        &format!(
                            "value between {} and {}",
                            MIN.as_secs(),
                            MAX.as_secs()
                        )
                        .as_str(),
                    ))
                }
            }
        }

        deserializer.deserialize_f64(FadeTimeVisitor)
    }
}
