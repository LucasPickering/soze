mod api;
mod color;
mod reducer;

use crate::{
    api::{routes::get_router, state::UserState},
    reducer::{
        resource::{LcdResource, LedResource, Resource},
        state::{KeepaliveState, LcdHardwareState, LedHardwareState},
    },
};
use std::sync::Arc;
use tokio::sync::RwLock;

#[tokio::main]
async fn main() {
    // Initialize state
    let user_state = arc_lock(UserState::load().await.unwrap());
    let keepalive_state = arc_lock(KeepaliveState::default());
    let led_hardware_state = arc_lock(LedHardwareState::default());
    let lcd_hardware_state = arc_lock(LcdHardwareState::default());

    // Start the reducer
    LedResource::spawn(&user_state, &keepalive_state, &led_hardware_state);
    LcdResource::spawn(&user_state, &keepalive_state, &lcd_hardware_state);

    // Start the API
    let app = get_router(user_state);
    axum::Server::bind(&"127.0.0.1:5000".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}

fn arc_lock<T>(value: T) -> Arc<RwLock<T>> {
    Arc::new(RwLock::new(value))
}
