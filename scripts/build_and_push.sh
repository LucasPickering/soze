#!/bin/sh

set -e

docker buildx bake --set '*.platform=linux/arm/v6' -f docker-compose.build.yml $@
docker-compose -f docker-compose.build.yml push
