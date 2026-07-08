#!/bin/bash

# Default value
USE_GPU="true"

# Check if the --no-gpu argument is passed
if [ "$1" == "--no-gpu" ]; then
    USE_GPU="false"
fi

echo "Building image with USE_GPU=$USE_GPU..."

# Run the build command
docker build \
    --build-arg USE_GPU=$USE_GPU \
    -t ros2_fossbot_edu_yolo \
    -f object_detection/Dockerfile .