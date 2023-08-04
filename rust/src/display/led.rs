use crate::{display::Hardware, state::hardware::LedState};
use anyhow::Context;
use async_trait::async_trait;
use tokio::{io::AsyncWriteExt, net::UnixStream, sync::RwLock};

const SOCKET_PATH: &str = "soze-led";

pub struct LedHardware {
    #[cfg(not(hardware))]
    socket: tokio::net::UnixStream,
}

/// Mock implementation
#[cfg(not(hardware))]
#[async_trait]
impl Hardware for LedHardware {
    type State = LedState;

    async fn new() -> anyhow::Result<Self> {
        Ok(Self {
            socket: UnixStream::connect(SOCKET_PATH).await.with_context(
                || format!("Error opening LED socket `{SOCKET_PATH}`"),
            )?,
        })
    }

    async fn on_tick(
        &mut self,
        state: &RwLock<Self::State>,
    ) -> anyhow::Result<()> {
        let color = state.read().await.color;
        self.socket.write_all(&color.to_bytes()).await?;
        Ok(())
    }
}
