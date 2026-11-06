# Use official ROS2 Jazzy desktop full image as the base image
FROM osrf/ros:jazzy-desktop-full

# Install dependencies for GUI display and tools (RViz, Gazebo, etc.)
RUN apt-get update && apt-get install -y \
    x11-apps \
    libgl1 \
    libgl1-mesa-dri \
    mesa-utils \
    build-essential \
    git \
    curl \
    wget \
    nano \
    sudo \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    ros-jazzy-ros2-controllers \
    ros-jazzy-ros2-control \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-jazzy-slam-toolbox \
    ros-jazzy-teleop-twist-keyboard \
    ros-jazzy-twist-mux \
    ros-jazzy-joint-state-publisher \
    ros-jazzy-ros-gz \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-realsense2-description \
    ros-jazzy-realsense2-camera \
    ros-jazzy-sick-safetyscanners2 \
    ros-jazzy-sick-safetyscanners2-interfaces \
    && rm -rf /var/lib/apt/lists/*

# NVIDIA EGL ICD - fixes the black Gazebo window on Optimus setups
RUN mkdir -p /usr/share/glvnd/egl_vendor.d && \
    printf '%s' '{"file_format_version":"1.0.0","ICD":{"library_path":"libEGL_nvidia.so.0"}}' \
    > /usr/share/glvnd/egl_vendor.d/10_nvidia.json

# Set up environment for ROS2 and source it
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
SHELL ["/bin/bash", "-c"]

# pre-cache the Depot world from Gazebo Fuel (so depot.sdf loads offline)
RUN source /opt/ros/jazzy/setup.bash && \
    gz fuel download -u https://fuel.gazebosim.org/1.0/OpenRobotics/models/Depot \
    || echo "WARNING: Depot model not pre-cached (no internet at build time); it will download on first launch."

# Set the working directory to /fossbot_ros2 and copy the workspace
WORKDIR /fossbot_ros2

# Copy the fossbot_ws folder from the host into the Docker image
COPY ws_fossbot /fossbot_ros2/ws_fossbot

# Set the working directory to the workspace
WORKDIR /fossbot_ros2/ws_fossbot

# Build the workspace
RUN source /opt/ros/jazzy/setup.bash && \
    rosdep update && \
    rosdep install --from-paths src --ignore-src -r -y || true

# Build the workspace using colcon
RUN source /opt/ros/jazzy/setup.bash && colcon build --symlink-install

RUN echo "source /fossbot_ros2/ws_fossbot/install/setup.bash" >> ~/.bashrc

# Keep ROS 2 and Gazebo discovery on localhost so lab PCs on one network don't share topics
ENV ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
ENV GZ_IP=127.0.0.1

# Exporting a robot's ROS_DOMAIN_ID (see "Connecting to real robot") switches the shell to subnet
# discovery so the group can reach the bridge; domain 0 (the simulation) stays on localhost
RUN printf '%s\n' \
    '_fossbot_discovery_range() {' \
    '    [ "$ROS_AUTOMATIC_DISCOVERY_RANGE" = "${_FOSSBOT_RANGE:-LOCALHOST}" ] || return 0' \
    '    if [ "${ROS_DOMAIN_ID:-0}" = 0 ]; then _FOSSBOT_RANGE=LOCALHOST; else _FOSSBOT_RANGE=SUBNET; fi' \
    '    export ROS_AUTOMATIC_DISCOVERY_RANGE=$_FOSSBOT_RANGE' \
    '}' \
    'trap _fossbot_discovery_range DEBUG' >> ~/.bashrc
