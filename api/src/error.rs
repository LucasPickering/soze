use log::{log, Level};
use rocket::{http::Status, response::Responder, Request};
use std::{backtrace::Backtrace, error::Error};
use thiserror::Error;

pub type ApiResult<T> = Result<T, ApiError>;

/// Any recoverable error type that can occur during API operation (i.e.
/// while handling a request).
#[derive(Debug, Error)]
pub enum ApiError {
    #[error("database error: {source}")]
    Redis {
        #[from]
        source: redis::RedisError,
        backtrace: Backtrace,
    },

    #[error("error serializing/deserializing data to/from database: {source}")]
    RedisSerialize {
        #[from]
        source: serde_json::Error,
        backtrace: Backtrace,
    },
}

impl ApiError {
    /// Convert this error to an HTTP status code
    pub fn to_status(&self) -> Status {
        match self {
            // 500
            Self::Redis { .. } | Self::RedisSerialize { .. } => {
                Status::InternalServerError
            }
        }
    }

    /// Log this error. Logging level will be based on the status code
    pub fn log(&self) {
        let log_level = if self.to_status().code >= 500 {
            Level::Error
        } else {
            Level::Debug
        };

        log!(
            log_level,
            "API Error: {}\n{}",
            self,
            self.backtrace().expect("No backtrace available :(")
        );
    }
}

impl<'r> Responder<'r, 'static> for ApiError {
    fn respond_to(
        self,
        _: &'r Request<'_>,
    ) -> rocket::response::Result<'static> {
        self.log();
        Err(self.to_status())
    }
}
