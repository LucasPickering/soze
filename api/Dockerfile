# Version doesn't matter here since we use a nightly from rust-toolchain
FROM rust:slim

WORKDIR /app/api
COPY rust-toolchain .
# This cmd will also install whatever toolchain we need
RUN cargo install cargo-watch
