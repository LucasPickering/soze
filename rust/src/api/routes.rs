use crate::{
    api::error::ApiResult,
    resource::{LcdResource, LedResource, Resource},
    state::{
        common::Status,
        user::{AllResourceState, ResourceState},
    },
};
use axum::{
    extract::{Path, State},
    response::Redirect,
    routing::{get, post},
    Json, Router,
};
use std::sync::Arc;
use tokio::sync::RwLock;

type RouteState = State<Arc<RwLock<AllResourceState>>>;

pub fn get_router(user_state: Arc<RwLock<AllResourceState>>) -> Router {
    Router::new()
        .route("/led", get(get_resource_state::<LedResource>))
        .route("/lcd", get(get_resource_state::<LcdResource>))
        .route("/led/:status", get(get_resource_status::<LedResource>))
        .route("/lcd/:status", get(get_resource_status::<LcdResource>))
        .route("/led/:status", post(set_resource_status::<LedResource>))
        .route("/lcd/:status", post(set_resource_status::<LcdResource>))
        // Mission critical
        .route(
            "/xkcd",
            get(|| async {
                Redirect::permanent("https://c.xkcd.com/random/comic")
            }),
        )
        .with_state(user_state)
}

// These routes are all generic, and are instantiated once per resource

/// Get resource state for all statuses
async fn get_resource_state<R: Resource>(
    State(user_state): RouteState,
) -> Json<ResourceState<R::UserState>> {
    let state = user_state.read().await;
    Json(R::get_user_state(&state).clone())
}

/// Get resource state for an individual status
async fn get_resource_status<R: Resource>(
    Path(status): Path<Status>,
    State(user_state): RouteState,
) -> Json<R::UserState> {
    let state = user_state.read().await;
    Json(R::get_user_state(&state).get(status).clone())
}

/// Set resource state for an individual status
async fn set_resource_status<R: Resource>(
    Path(status): Path<Status>,
    State(user_state): RouteState,
    Json(new_state): Json<R::UserState>,
) -> ApiResult<Json<R::UserState>> {
    let mut state = user_state.write().await;
    *R::get_user_state_mut(&mut state).get_mut(status) = new_state.clone();
    state.downgrade().save().await?;
    Ok(Json(new_state))
}
