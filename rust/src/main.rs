mod api;
mod reducer;

use crate::{
    api::{routes::get_router, state::UserState},
    reducer::{
        resource::{LedResource, Resource},
        state::HardwareState,
    },
};
use std::sync::Arc;
use tokio::sync::RwLock;

#[tokio::main]
async fn main() {
    let user_state = Arc::new(RwLock::new(UserState::load().await.unwrap()));
    let hardware_state = Arc::new(RwLock::new(HardwareState::default()));

    // Start the reducer
    LedResource::spawn(Arc::clone(&user_state), Arc::clone(&hardware_state));

    // Start the API
    let app = get_router(user_state);
    axum::Server::bind(&"127.0.0.1:5000".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}
