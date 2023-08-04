use crate::{display::Hardware, state::hardware::KeepaliveState};
use async_trait::async_trait;
use std::time::Duration;
use tokio::sync::RwLock;

pub struct KeepaliveHardware;

/// Mock implementation
#[cfg(not(hardware))]
#[async_trait]
impl Hardware for KeepaliveHardware {
    const INTERVAL: Duration = Duration::from_millis(1000); // Slow boi
    type State = KeepaliveState;

    async fn new() -> anyhow::Result<Self> {
        Ok(Self)
    }

    #[cfg(not(hardware))]
    async fn on_tick(
        &mut self,
        state: &RwLock<Self::State>,
    ) -> anyhow::Result<()> {
        // TODO should we read this from a file maybe? set via signals? UDS?
        state.write().await.is_alive = true;
        Ok(())
    }
}
