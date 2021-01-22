use crate::{
    error::ApiResult,
    resource::{ResourceSettings, Status},
};
use redis::AsyncCommands;
use std::collections::HashMap;
use strum::IntoEnumIterator;

/// A singleton struct to handle all interaction with the Redis database.
pub struct DatabaseHandler {
    redis_client: redis::Client,
}

impl DatabaseHandler {
    pub fn new(redis_host: &str) -> ApiResult<Self> {
        let redis_client = redis::Client::open(redis_host)?;
        Ok(Self { redis_client })
    }

    /// Load settings from the database for a single resource/status pairing.
    pub async fn load<R: ResourceSettings>(
        &self,
        status: Status,
    ) -> ApiResult<R> {
        let redis_key = Self::redis_key::<R>(status);
        let mut conn = self.redis_client.get_async_connection().await?;
        // Grab data from redis and deserialize. If it's not present, just use
        // the default value.
        let data: Option<String> = conn.get(&redis_key).await?;
        let settings: R = match data {
            Some(data) => serde_json::from_str(&data)?,
            None => R::default(),
        };
        Ok(settings)
    }

    /// Load all of a resources settings objects (one per status).
    pub async fn load_all<R: ResourceSettings>(
        &self,
    ) -> ApiResult<HashMap<Status, R>> {
        // Execute each status's DB query concurrently
        let futures = Status::iter().map(|status| self.load(status));
        let data = futures::future::try_join_all(futures).await?;

        let settings: HashMap<_, _> = Status::iter().zip(data).collect();
        Ok(settings)
    }

    /// Modify settings in the database for a particular resource/status combo.
    pub async fn update<R: ResourceSettings>(
        &self,
        status: Status,
        settings: R,
    ) -> ApiResult<R> {
        let redis_key = Self::redis_key::<R>(status);
        let pub_channel = Self::redis_publish_channel::<R>();
        let data = serde_json::to_string(&settings)?;

        // Set the data in redis and publish to notify the reducer
        let mut conn = self.redis_client.get_async_connection().await?;
        conn.set::<'_, _, _, ()>(&redis_key, data).await?;
        conn.publish::<'_, _, _, ()>(&pub_channel, "").await?;

        Ok(settings)
    }

    /// The key that data is stored under for a particular resource+status.
    fn redis_key<R: ResourceSettings>(status: Status) -> String {
        format!("user:{}:{}", R::name(), status)
    }

    /// The channel to publish events on after modifying a resource. This
    /// channel should be used regardless of which status is modified.
    fn redis_publish_channel<R: ResourceSettings>() -> String {
        format!("a2r:{}", R::name(),)
    }
}
