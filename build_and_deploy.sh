#!/bin/bash

# This isn't part of the Dockerfile because then it would run on the RPi
if [[ "$@" = "" || " $@ " =~ " webserver " ]]; then
    ( cd webapp; npm run build )
fi

docker-compose -f docker-compose.pi.yml build $@
docker-compose -f docker-compose.pi.yml up -d
