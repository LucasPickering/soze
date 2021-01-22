# Version doesn't matter here since we use a nightly from rust-toolchain
FROM rust:slim AS builder

WORKDIR /app/api
COPY . .
RUN cargo build --release

FROM debian:buster-slim
WORKDIR /app/api
COPY --from=builder /app/api/target/release/soze-api .
CMD ["/app/api/soze-api"]
