use crate::api::{
    error::ApiResult,
    state::{LcdState, LedState, Resource, Status, UserState},
};
use axum::{
    extract::{Path, State},
    response::Redirect,
    routing::{get, post},
    Json, Router,
};
use std::sync::Arc;
use tokio::sync::RwLock;

type RouteUserState = State<Arc<RwLock<UserState>>>;

pub fn get_router(user_state: Arc<RwLock<UserState>>) -> Router {
    Router::new()
        .route("/led", get(get_led))
        .route("/lcd", get(get_lcd))
        .route("/led/:status", get(get_led_status))
        .route("/lcd/:status", get(get_lcd_status))
        .route("/led/:status", post(set_led_status))
        .route("/lcd/:status", post(set_lcd_status))
        // Mission critical
        .route(
            "/xkcd",
            get(|| async {
                Redirect::permanent("https://c.xkcd.com/random/comic")
            }),
        )
        .with_state(user_state)
}

/// Get LED state for all statuses
async fn get_led(
    State(user_state): RouteUserState,
) -> Json<Resource<LedState>> {
    let state = user_state.read().await;
    Json(state.led.clone())
}

/// Get LCD state for all statuses
async fn get_lcd(
    State(user_state): RouteUserState,
) -> Json<Resource<LcdState>> {
    let state = user_state.read().await;
    Json(state.lcd.clone())
}

/// Get LED state for an individual status
async fn get_led_status(
    Path(status): Path<Status>,
    State(user_state): RouteUserState,
) -> Json<LedState> {
    let state = user_state.read().await;
    Json(state.led.get(status).clone())
}

/// Get LCD state for an individual status
async fn get_lcd_status(
    Path(status): Path<Status>,
    State(user_state): RouteUserState,
) -> Json<LcdState> {
    let state = user_state.read().await;
    Json(*state.lcd.get(status))
}

/// Get LED state for an individual status
async fn set_led_status(
    Path(status): Path<Status>,
    State(user_state): RouteUserState,
    Json(new_state): Json<LedState>,
) -> ApiResult<Json<LedState>> {
    let mut state = user_state.write().await;
    *state.led.get_mut(status) = new_state.clone();
    state.downgrade().save().await?;
    Ok(Json(new_state))
}

/// Get LED state for an individual status
async fn set_lcd_status(
    Path(status): Path<Status>,
    State(user_state): RouteUserState,
    Json(new_state): Json<LcdState>,
) -> ApiResult<Json<LcdState>> {
    let mut state = user_state.write().await;
    *state.lcd.get_mut(status) = new_state;
    state.downgrade().save().await?;
    Ok(Json(new_state))
}
