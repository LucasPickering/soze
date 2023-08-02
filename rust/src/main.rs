mod api;
mod resource;
mod state;

use crate::{
    api::routes::get_router,
    resource::{lcd::LcdResource, led::LedResource, Resource},
    state::{
        hardware::{self, KeepaliveState},
        user::AllResourceState,
    },
};
use std::sync::Arc;
use tokio::sync::RwLock;

#[tokio::main]
async fn main() {
    // Initialize API state
    let user_state = arc_lock(AllResourceState::load().await.unwrap());

    // Initialize hardware state
    let keepalive_state = arc_lock(KeepaliveState::default());
    let led_hardware_state = arc_lock(hardware::LedState::default());
    let lcd_hardware_state = arc_lock(hardware::LcdState::default());

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
