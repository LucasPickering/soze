//! Interfaces for the hardware. Each of these has both a real version and a
//! mock version. You can switch between the two using the "hardware" feature
//! flag.
//!
//! The real versions interface directly with the hardware. The mock versions
//! communicate with the interactive mock display via Unix Domain Sockets.
//! Except for the keepalive, which just reads a file input.

use async_trait::async_trait;
use log::info;
use std::{sync::Arc, time::Duration};
use tokio::{sync::RwLock, time};

pub mod keepalive;
pub mod lcd;
pub mod led;

// TODO better name than display (can we take back `hardware`?)

/// Interface for a display device. Data is sent from the reducer to the
/// hardware. The methods on this are async and fallible because they require
/// interacting outside this process, unlike the reducer.
#[async_trait]
pub trait Hardware: Send + Sized {
    const NAME: &'static str;
    /// Frequency at which to update hardware
    const INTERVAL: Duration = Duration::from_millis(100);
    type State: 'static + Send + Sync;

    async fn new() -> anyhow::Result<Self>;

    /// Run a loop to sync between state and the hardware. If there are any
    /// errors during hardware initialization or syncing, this will repeatedly
    /// reinitialize in a loop, for ease of development.
    async fn run(state: &Arc<RwLock<Self::State>>) -> anyhow::Result<()> {
        let state = Arc::clone(state);

        // Run a loop to update the hardware
        info!("Initializing hardware {}", Self::NAME);
        let mut interval = time::interval(Self::INTERVAL);
        let mut resource = Self::new().await?;
        loop {
            resource.on_tick(&state).await?;
            interval.tick().await;
        }
    }

    /// Update hardware/state on a fixed interval
    async fn on_tick(
        &mut self,
        state: &RwLock<Self::State>,
    ) -> anyhow::Result<()>;
}
