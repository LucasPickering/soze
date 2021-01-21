#!/bin/sh

docker buildx bake --set '*.platform=linux/arm/v6' -f docker-compose.build.yml --push $@
