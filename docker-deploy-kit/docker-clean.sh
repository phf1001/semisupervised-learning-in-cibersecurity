#!/bin/bash

docker-compose down -v > /dev/null 2>&1
docker kill $(docker ps -q) > /dev/null 2>&1
docker rmi -f $(docker images -q) > /dev/null 2>&1
docker-compose down -v > /dev/null 2>&1