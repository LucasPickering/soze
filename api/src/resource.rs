//! A resource is a single piece of hardware that we control from Söze. This
//! module defines some generic types for resources, as well as types for the
//! possible user-configurable settings that each resource supports.

use crate::color::Color;
use rocket::{http::RawStr, request::FromParam};
use serde::{de::DeserializeOwned, Deserialize, Serialize};
use std::collections::HashMap;
use strum::{Display, EnumIter, EnumString};
use validator::Validate;

/// A "status" defines a particular mode of the system. Each resource can have
/// one settings object for each status. This allows you to define hardware
/// settings that vary based on the state of the PC. E.g. you can have
/// everything turn off when the PC is put to sleep.
#[derive(
    Copy,
    Clone,
    Debug,
    Display,
    PartialEq,
    Eq,
    Hash,
    EnumString,
    EnumIter,
    Serialize,
)]
#[strum(serialize_all = "snake_case")]
#[serde(rename_all = "snake_case")]
pub enum Status {
    /// PC is running normally
    Normal,
    /// PC is asleep/off (no 12V power coming from the PSU)
    Sleep,
}

// Allow Status to be a URL param
impl<'r> FromParam<'r> for Status {
    type Error = &'r RawStr;

    fn from_param(param: &'r RawStr) -> Result<Self, Self::Error> {
        // parse the value as a status name
        let s = param.url_decode().map_err(|_| param)?;
        s.parse().map_err(|_| param)
    }
}

/// Settings for a hardware resource. Each resource has a dedicated name and
/// its settings are serializable and deserializable.
///
/// Each settings type defines all the configurable fields for a particular
/// resource. These settings objects are user-readable and user-writable. In
/// most cases, the type of the setting alone is sufficient to validate user
/// input. In cases where you want to define more stringent requirements (e.g.
/// define a valid range for a number), you can use the
/// [Validate](validator::Validate) trait.
pub trait ResourceSettings:
    Default + Serialize + DeserializeOwned + Validate
{
    fn name() -> &'static str;
}

// ===== LED Settings =====

/// Settings for an RGB LED strip.
#[derive(Clone, Debug, Default, Serialize, Deserialize, Validate)]
pub struct LedSettings {
    mode: LedMode,
    #[serde(rename = "static")]
    static_: LedStaticSettings,
    fade: LedFadeSettings,
}

#[derive(Copy, Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LedMode {
    Off,
    Static,
    Fade,
}

/// Settings for when the LEDs are in static mode. The LEDs will hold just a
/// single color.
#[derive(Clone, Debug, Default, Serialize, Deserialize, Validate)]
pub struct LedStaticSettings {
    color: Color,
}

/// Settings for when the LEDs are in fade mode. The LEDs will fade between a
/// list of multiple colors.
#[derive(Clone, Debug, Serialize, Deserialize, Validate)]
pub struct LedFadeSettings {
    /// The colors to fade between
    colors: Vec<Color>,
    /// A map of saved "fade sets", to make it easy to switch between different
    /// LED color lists. This map is just a convenience for the user, and these
    /// values will never be directly used by the hardware.
    saved: HashMap<String, Vec<Color>>,
    /// The amount of time to spend transitioning from one color to the next in
    /// the list.
    #[validate(range(min = 1.0, max = 30.0))]
    fade_time: f32,
}

impl ResourceSettings for LedSettings {
    fn name() -> &'static str {
        "led"
    }
}

impl Default for LedMode {
    fn default() -> Self {
        Self::Off
    }
}

impl Default for LedFadeSettings {
    fn default() -> Self {
        Self {
            colors: Vec::new(),
            saved: HashMap::new(),
            fade_time: 5.0,
        }
    }
}

// ===== LCD Settings =====

/// Settings for a character LCD with RGB backlighting.
#[derive(Clone, Debug, Default, Serialize, Deserialize, Validate)]
pub struct LcdSettings {
    mode: LcdMode,
    color: Color,
}

#[derive(Copy, Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LcdMode {
    Off,
    Clock,
}

impl ResourceSettings for LcdSettings {
    fn name() -> &'static str {
        "lcd"
    }
}

impl Default for LcdMode {
    fn default() -> Self {
        Self::Off
    }
}
