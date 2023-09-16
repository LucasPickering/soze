#!/bin/sh

HOST=$1

DOCKER_HOST=ssh://$HOST docker-compose -f docker-compose.pi.yml up -d
