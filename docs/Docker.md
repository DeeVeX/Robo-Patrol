# Setup ROS and Robopatrol with Docker

## 1. Install Docker

Windows and Linux: `https://docs.docker.com/engine/installation/`

Using Homebrew on OS X: `brew install docker docker-machine docker-compose`

## 2. Create docker-machine

Linux can run Docker without a `docker-machine` VM. So Linux users may skip this part.

On OS X and Windows this needs to be done **once**:

Virtualbox example: `docker create ros --driver virtualbox` 

## 2. Launch

Tell Docker to use the docker-machine: `eval $(docker-machine env ros)`

```shell
docker-compose build
docker-compose up
```

Interactive launch (e.g. to run tests or try something out):

```shell
docker-compose run robopatrol /bin/bash
``` 