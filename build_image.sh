#!/bin/bash
# Build the image with a user matching the host user's UID/GID, so files created
# inside the container in the mounted workspace are owned by you on the host.
docker build \
    --build-arg USER_UID=$(id -u) \
    --build-arg USER_GID=$(id -g) \
    -t ros2_fossbot_edu .
