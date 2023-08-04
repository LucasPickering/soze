use crate::{display::Hardware, state::hardware::LcdState};
use anyhow::Context;
use async_trait::async_trait;
use log::trace;
use tokio::{io::AsyncWriteExt, net::UnixStream, sync::RwLock};

const SOCKET_PATH: &str = "/tmp/soze-lcd";

pub struct LcdHardware {
    #[cfg(not(hardware))]
    socket: tokio::net::UnixStream,
}

/// Mock implementation
#[cfg(not(hardware))]
#[async_trait]
impl Hardware for LcdHardware {
    const NAME: &'static str = "LCD";
    type State = LcdState;

    async fn new() -> anyhow::Result<Self> {
        Ok(Self {
            socket: UnixStream::connect(SOCKET_PATH).await.with_context(
                || format!("Error opening LCD socket `{SOCKET_PATH}`"),
            )?,
        })
    }

    async fn on_tick(
        &mut self,
        state: &RwLock<Self::State>,
    ) -> anyhow::Result<()> {
        // Write all bytes, then clear the queue. Make sure to hold a write lock
        // the whole time, so no one can write bytes before we clear
        let message_queue = &mut state.write().await.message_queue;
        if !message_queue.is_empty() {
            trace!("Writing LCD bytes: {message_queue:x?}");
            self.socket.write_all(message_queue).await?;
            message_queue.clear();
        }
        Ok(())
    }
}
