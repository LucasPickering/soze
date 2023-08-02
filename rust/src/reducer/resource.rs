use crate::{api::state::UserState, reducer::state::HardwareState};
use std::{
    ops::{Deref, DerefMut},
    sync::Arc,
    time::Duration,
};
use tokio::{sync::RwLock, time};

/// A hardware resource (LED or LCD). This will regularly update hardware state
/// based on user state and external state (e.g. current time).
///
/// Each resource needs to be spawned separately and will run on a fixed
/// interval.
pub trait Resource {
    const INTERVAL: Duration = Duration::from_millis(100);

    /// Spawn an async task that will update hardware state on a regular
    /// interval.
    fn spawn(
        user_state: Arc<RwLock<UserState>>,
        hardware_state: Arc<RwLock<HardwareState>>,
    ) {
        // Run the updater function on a regular interval, to keep hardware
        // state in sync with user state.
        //
        tokio::spawn(async move {
            let mut interval = time::interval(Self::INTERVAL);
            loop {
                Self::update(
                    user_state.read().await.deref(),
                    hardware_state.write().await.deref_mut(),
                );
                interval.tick().await;
            }
        });
    }

    /// Update hardware state based on the current user state. We're being lazy
    /// here and grabbing the locks before calling, because it avoids this
    /// neeing to be async, which would pull in async_trait. This means our lock
    /// period is longer than it needs to be, but we're running every 100ms so
    /// it's fine.
    fn update(user_state: &UserState, hardware_state: &mut HardwareState);
}

pub struct LedResource;

impl Resource for LedResource {
    fn update(user_state: &UserState, hardware_state: &mut HardwareState) {
        todo!()
    }
}

pub struct LcdResource;

impl Resource for LcdResource {
    fn update(user_state: &UserState, hardware_state: &mut HardwareState) {
        todo!()
    }
}
