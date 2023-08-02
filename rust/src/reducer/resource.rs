use crate::{
    api::state::{Status, UserState},
    reducer::state::{KeepaliveState, LcdHardwareState, LedHardwareState},
};
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

    /// Type of state that we expect to be modifying.
    type HardwareState: 'static + Send + Sync;

    /// Spawn an async task that will update hardware state on a regular
    /// interval.
    fn spawn(
        user_state: &Arc<RwLock<UserState>>,
        keepalive: &Arc<RwLock<KeepaliveState>>,
        hardware_state: &Arc<RwLock<Self::HardwareState>>,
    ) {
        let user_state = Arc::clone(user_state);
        let keepalive = Arc::clone(keepalive);
        let hardware_state = Arc::clone(hardware_state);
        tokio::spawn(async move {
            let mut interval = time::interval(Self::INTERVAL);
            loop {
                let status = keepalive.read().await.to_status();
                Self::update(
                    status,
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
    fn update(
        status: Status,
        user_state: &UserState,
        hardware_state: &mut Self::HardwareState,
    );
}

pub struct LedResource;

impl Resource for LedResource {
    type HardwareState = LedHardwareState;

    fn update(
        status: Status,
        user_state: &UserState,
        hardware_state: &mut Self::HardwareState,
    ) {
        todo!()
    }
}

pub struct LcdResource;

impl Resource for LcdResource {
    type HardwareState = LcdHardwareState;

    fn update(
        status: Status,
        user_state: &UserState,
        hardware_state: &mut Self::HardwareState,
    ) {
        todo!()
    }
}
