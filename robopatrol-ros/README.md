# Base Docker Image

This docker image is the basis for our other Docker images.

We start from the official ros Docker image and then install a few more tools to get our builds to run. The image is uploaded to the Docker Hub in order to make our other docker builds run faster.

## Uploading New Builds
```
docker build -t robopatrol/robopatrol-base
docker push robopatrol/robopatrol-base
```
