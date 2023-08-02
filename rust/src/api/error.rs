use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use std::{collections::HashMap, io, num::ParseIntError};
use thiserror::Error;

pub type ApiResult<T> = Result<T, ApiError>;

/// All error types that can occur during API operation. These can be converted
/// into status codes.
#[derive(Debug, Error)]
pub enum ApiError {
    #[error(transparent)]
    Io(#[from] io::Error),

    #[error("Invalid input: {input}")]
    Validation { input: String },
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        // Convert error type into status code
        let (status, error_message) = match self {
            Self::Io(_) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                "Internal server error".to_owned(),
            ),
            Self::Validation { input } => (StatusCode::BAD_REQUEST, input),
        };

        let body = Json(HashMap::from([("error", error_message)]));
        (status, body).into_response()
    }
}

impl From<ParseIntError> for ApiError {
    fn from(value: ParseIntError) -> Self {
        // This is kinda shitty because we're throwing away error context, but
        // who cares
        Self::Validation {
            input: value.to_string(),
        }
    }
}
