#!/bin/bash

# This isn't part of the Dockerfile because then it would run on the RPi
if [[ "$@" = "" || " $@ " =~ " webserver " ]]; then
    docker-compose -f docker-compose.build.yml build
    docker-compose -f docker-compose.build.yml push
fi

docker-compose -f docker-compose.pi.yml build $@
docker-compose -f docker-compose.pi.yml up -d
