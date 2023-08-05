mod api;
mod display;
mod resource;
mod state;

use crate::{
    api::routes::get_router,
    display::{
        keepalive::KeepaliveHardware, lcd::LcdHardware, led::LedHardware,
        Hardware,
    },
    resource::{lcd::LcdResource, led::LedResource, Resource},
    state::{
        hardware::{self, KeepaliveState},
        user::AllResourceState,
    },
};
use log::{error, LevelFilter};
use std::{future::Future, sync::Arc};
use tokio::{join, sync::RwLock};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    env_logger::builder()
        .filter_level(LevelFilter::Trace)
        .init();

    // Initialize API state
    let user_state = arc_lock(AllResourceState::load().await.unwrap());

    // Initialize hardware state
    let keepalive_state = arc_lock(KeepaliveState::default());
    let led_hardware_state = arc_lock(hardware::LedState::default());
    let lcd_hardware_state = arc_lock(hardware::LcdState::default());

    // Start all the concurrent tasks together. If any task fails, we'll log it
    // without killing everything else
    join!(
        // API
        log_result(
            "API",
            axum::Server::bind(&"127.0.0.1:5000".parse().unwrap())
                .serve(get_router(Arc::clone(&user_state)).into_make_service())
        ),
        // Reducer
        log_result(
            "LED Reducer",
            LedResource::run(
                &user_state,
                &keepalive_state,
                &led_hardware_state,
            )
        ),
        log_result(
            "LCD Reducer",
            LcdResource::run(
                &user_state,
                &keepalive_state,
                &lcd_hardware_state,
            )
        ),
        // Hardware
        log_result(
            "Keepalive Hardware",
            KeepaliveHardware::run(&keepalive_state)
        ),
        log_result("LED Hardware", LedHardware::run(&led_hardware_state)),
        log_result("LCD Hardware", LcdHardware::run(&lcd_hardware_state)),
    );
    Ok(())
}

/// Await a future, and if it fails, log the error
async fn log_result<T, E: Into<anyhow::Error>>(
    task_name: &str,
    future: impl Future<Output = Result<T, E>>,
) {
    if let Err(err) = future.await {
        let err: anyhow::Error = err.into();
        error!("{task_name} task failed: {err:#}\n{}", err.backtrace());
    }
}

fn arc_lock<T>(value: T) -> Arc<RwLock<T>> {
    Arc::new(RwLock::new(value))
}
