#!/bin/bash

docker-compose -f niu_heimar.yml down
docker system prune -f
docker container rm -f $(docker container ls -aq)

commands=$1
if [[ $commands == *"rmi"* ]]; then
  docker image rm -f $(docker image ls -aq)
fi

docker system info
