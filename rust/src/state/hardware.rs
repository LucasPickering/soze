//! State between the reducer and hardware layers. This state is broken into
//! different structs so that each resource task can access them independently
//! without lock contention.

use crate::state::common::{RgbColor, Status};

/// Keepalive flag, which monitors when the parent PC is on. This will control
/// the current [Status](crate::api::state::Status) of the reducer.
#[derive(Debug, Default)]
pub struct KeepaliveState {
    is_alive: bool,
}

impl KeepaliveState {
    pub fn to_status(&self) -> Status {
        if self.is_alive {
            Status::Normal
        } else {
            Status::Sleep
        }
    }
}

/// State of LED hardware
#[derive(Debug, Default)]
pub struct LedState {
    color: RgbColor,
}

/// LCD state is stored as an imperative queue instead of declarative state.
/// This frontloads logic into the reducer, and makes it easier to do
/// event-based logic like "turn off the LCD on shutdown".
#[derive(Debug, Default)]
pub struct LcdState {
    command_queue: Vec<u8>,
}
