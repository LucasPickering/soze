pub mod lcd;
pub mod led;

use crate::state::{hardware, user};
use serde::{Deserialize, Serialize};
use std::{ops::DerefMut, sync::Arc, time::Duration};
use tokio::{sync::RwLock, time};

/// A hardware resource (LED or LCD). This captures all generic logic for a
/// resource, including how to extract and update its state.
///
/// Each resource will have a separate async task spawned, which will run on a
/// fixed interval.
pub trait Resource: Default + Send {
    const INTERVAL: Duration = Duration::from_millis(100);

    /// Type of state managed by the user/API
    type UserState: 'static
        + Clone
        + Send
        + Sync
        + Serialize
        + Deserialize<'static>;
    /// Type of state that we expect to be modifying.
    type HardwareState: 'static + Send + Sync;

    /// Spawn an async task that will update hardware state on a regular
    /// interval.
    fn spawn(
        all_resource_state: &Arc<RwLock<user::AllResourceState>>,
        keepalive: &Arc<RwLock<hardware::KeepaliveState>>,
        hardware_state: &Arc<RwLock<Self::HardwareState>>,
    ) {
        let all_resource_state = Arc::clone(all_resource_state);
        let keepalive = Arc::clone(keepalive);
        let hardware_state = Arc::clone(hardware_state);
        tokio::spawn(async move {
            let mut interval = time::interval(Self::INTERVAL);
            let mut resource = Self::default();
            loop {
                let status = keepalive.read().await.to_status();
                let all_resource_state = all_resource_state.read().await;
                // Select current user state based on this resource+status
                let user_state =
                    Self::get_user_state(&all_resource_state).get(status);
                resource.update(
                    user_state,
                    hardware_state.write().await.deref_mut(),
                );
                interval.tick().await;
            }
        });
    }

    /// Extract user state for this particular resource, from the global user
    /// state object
    fn get_user_state(
        global_state: &user::AllResourceState,
    ) -> &user::ResourceState<Self::UserState>;

    /// Extract a mutable reference to user state for this particular resource,
    /// from the global user state object. Unfortunate that we have to duplicate
    /// this.
    fn get_user_state_mut(
        global_state: &mut user::AllResourceState,
    ) -> &mut user::ResourceState<Self::UserState>;

    /// Update hardware state based on the current user state. We're being lazy
    /// here and grabbing the locks before calling, because it avoids this
    /// neeing to be async, which would pull in async_trait. This means our lock
    /// period is longer than it needs to be, but we're running every 100ms so
    /// it's fine.
    fn update(
        &mut self,
        user_state: &Self::UserState,
        hardware_state: &mut Self::HardwareState,
    );
}
