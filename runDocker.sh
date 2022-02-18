#!/bin/bash

DOCKERNAME=${1:-"Worker1"}

docker build --tag projecto_final . &&
sleep 1
docker run  --name $DOCKERNAME projecto_final
