#!/bin/bash

YML_FILE=${1:-docker-compose.yml}

docker-compose -f $YML_FILE down
docker system prune
docker container rm -f $(docker container ls -aq)
# docker image rm -f $(docker image ls -aq)
docker system info
