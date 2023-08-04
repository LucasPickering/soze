use crate::{display::Hardware, state::hardware::LcdState};
use anyhow::Context;
use async_trait::async_trait;
use tokio::{io::AsyncWriteExt, net::UnixStream, sync::RwLock};

pub struct LcdHardware {
    #[cfg(not(hardware))]
    socket: tokio::net::UnixStream,
}

/// Mock implementation
#[cfg(not(hardware))]
#[async_trait]
impl Hardware for LcdHardware {
    type State = LcdState;

    async fn new() -> anyhow::Result<Self> {
        Ok(Self {
            socket: UnixStream::connect("soze-lcd")
                .await
                .context("Error opening LED socket")?,
        })
    }

    #[cfg(not(hardware))]
    async fn on_tick(
        &mut self,
        state: &RwLock<Self::State>,
    ) -> anyhow::Result<()> {
        // Write all bytes, then clear the queue. Make sure to hold a write lock
        // the whole time, so no one can write bytes before we clear
        let message_queue = &mut state.write().await.message_queue;
        self.socket.write_all(message_queue).await?;
        message_queue.clear();

        Ok(())
    }
}
