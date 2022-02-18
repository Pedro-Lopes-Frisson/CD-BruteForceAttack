#!/bin/bash
docker build --tag projecto_final . ; docker run --name woo111 projecto_final:latest  & docker run --name woo2 projecto_final:latest
