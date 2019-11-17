#!/bin/sh

docker-compose -f docker-compose.build.yml build
docker-compose -f docker-compose.build.yml push
