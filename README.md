# How to execute

Run the server in your host (not inside any container)

$ python3 main.py

Launch containers with 1 worker each (this is your code)

When you successfully guess the password, the worker will receive an image file.

# Using Docker

## Build your docker container

$ docker build --tag projecto_final .

## Launching containers

$ docker run -d --name worker1 projecto_final

## Monitor your containers

$ docker ps -a

## Stop your container

$ docker stop <container id>

## Remove old containers

$ docker rm <container id>

# Tips for install in Ubuntu:

$ sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev python3-openssl

## Objective
Crack a password using a distributed system by compilling everything we had previously learnt during both Theoretical and Practical Classes.

## How it was done
Nodes arranges in a network were an election process occured.
The elected node was meant to distribute work loads between nodes and keep track of the progress.
The server blacklisted some ip's in case of brute force attempting having in account the number of requests made by that ip.
Basic knowledge of dockers was required as well as HTTP headers composition.
## TODO
Complete the workload assignment as well as the tracking of the progress
