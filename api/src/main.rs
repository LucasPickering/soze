//! This API provides an interface for the user to read and modify hardware
//! settings. It exposes multiple resources (LEDs + LCD), and for each resource
//! provides a settings object for each status (see
//! [Status](crate::resource::Status)).

#![feature(backtrace)]

mod color;
mod db;
mod error;
mod resource;

use serde::Deserialize;
use crate::{
    db::DatabaseHandler,
    error::ApiResult,
    resource::{LcdSettings, LedSettings, Status},
};
use rocket::{get, put, routes, State};
use rocket_contrib::json::Json;
use std::collections::HashMap;

/// App-wide configuration settings
#[derive(Debug, Deserialize)]
pub struct ApiConfig {
    /// URL of the Redis instance
    pub redis_url: String,
}

/// Get settings for all statuses under the LED resource
#[get("/led")]
async fn get_led(
    db_handler: State<'_, DatabaseHandler>,
) -> ApiResult<Json<HashMap<Status, LedSettings>>> {
    let settings = db_handler.load_all().await?;
    Ok(Json(settings))
}

/// Get settings for a particular LED status
#[get("/led/<status>")]
async fn get_led_status(
    status: Status,
    db_handler: State<'_, DatabaseHandler>,
) -> ApiResult<Json<LedSettings>> {
    let settings = db_handler.load(status).await?;
    Ok(Json(settings))
}

/// Update settings for a particular LED status
#[put("/led/<status>", format = "json", data = "<body>")]
async fn put_led_status(
    status: Status,
    body: Json<LedSettings>,
    db_handler: State<'_, DatabaseHandler>,
) -> ApiResult<Json<LedSettings>> {
    let new_settings = db_handler.update(status, body.into_inner()).await?;
    Ok(Json(new_settings))
}

/// Get settings for all statuses under the LCD resource
#[get("/lcd")]
async fn get_lcd(
    db_handler: State<'_, DatabaseHandler>,
) -> ApiResult<Json<HashMap<Status, LcdSettings>>> {
    let settings = db_handler.load_all().await?;
    Ok(Json(settings))
}

/// Get settings for a particular LCD status
#[get("/lcd/<status>")]
async fn get_lcd_status(
    status: Status,
    db_handler: State<'_, DatabaseHandler>,
) -> ApiResult<Json<LcdSettings>> {
    let settings = db_handler.load(status).await?;
    Ok(Json(settings))
}

/// Update settings for a particular LCD status
#[put("/lcd/<status>", format = "json", data = "<body>")]
async fn put_lcd_status(
    status: Status,
    body: Json<LcdSettings>,
    db_handler: State<'_, DatabaseHandler>,
) -> ApiResult<Json<LcdSettings>> {
    let new_settings = db_handler.update(status, body.into_inner()).await?;
    Ok(Json(new_settings))
}

#[rocket::main]
async fn main() {
    env_logger::init();
    let rocket = rocket::ignite();
    let config: ApiConfig = rocket.figment().extract().unwrap();
    let db_handler = DatabaseHandler::new(&config.redis_url).unwrap();

    rocket
        .manage(db_handler)
        .mount(
            "/",
            routes![
                get_led,
                get_led_status,
                put_led_status,
                get_lcd,
                get_lcd_status,
                put_lcd_status
            ],
        )
        .launch()
        .await
        .unwrap();
}
