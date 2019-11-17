#!/bin/sh

docker-compose -f docker-compose.pi.yml pull $@
docker-compose -f docker-compose.pi.yml build $@
docker-compose -f docker-compose.pi.yml up -d
