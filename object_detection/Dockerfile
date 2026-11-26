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

# Non-root user matching the host user (UID/GID passed in by build_image.sh), so files
# created in the mounted workspace are owned by the host user instead of root
ARG USERNAME=fossbot
ARG USER_UID=1000
ARG USER_GID=1000

# Ubuntu 24.04 ships a 'ubuntu' user with UID/GID 1000 - remove it so ours can take that ID
RUN (userdel -r ubuntu 2>/dev/null || true) && \
    (getent group $USER_GID || groupadd -g $USER_GID $USERNAME) && \
    useradd -m -s /bin/bash -u $USER_UID -g $USER_GID -G video,dialout $USERNAME && \
    echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

SHELL ["/bin/bash", "-c"]

# Define the build argument
ARG USE_GPU=true
ENV IS_GPU_ENABLED=$USE_GPU

# Install additional Python packages
ENV PIP_BREAK_SYSTEM_PACKAGES=1
RUN if [ "$USE_GPU" = "true" ]; then \
        pip3 install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu132; \
    else \
        pip3 install --no-cache-dir torch torchvision; \
    fi && \
    pip3 install --no-cache-dir ultralytics "numpy<2.0.0"

# Copy the fossbot_ws folder from the host into the Docker image, owned by the user
COPY --chown=$USER_UID:$USER_GID ../ws_fossbot /fossbot_ros2/ws_fossbot
RUN chown $USER_UID:$USER_GID /fossbot_ros2

# Install system dependencies of the workspace (needs root)
RUN source /opt/ros/jazzy/setup.bash && \
    rosdep update && \
    rosdep install --from-paths /fossbot_ros2/ws_fossbot/src --ignore-src -r -y || true

# Everything below runs as the user
USER $USERNAME
WORKDIR /fossbot_ros2/ws_fossbot

RUN rosdep update

# pre-cache the Depot world from Gazebo Fuel (so depot.sdf loads offline); cached in ~/.gz
RUN source /opt/ros/jazzy/setup.bash && \
    gz fuel download -u https://fuel.gazebosim.org/1.0/OpenRobotics/models/Depot \
    || echo "WARNING: Depot model not pre-cached (no internet at build time); it will download on first launch."

# Build the workspace using colcon
RUN source /opt/ros/jazzy/setup.bash && colcon build --symlink-install

# Set up environment for ROS2 and source it
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc && \
    echo "source /fossbot_ros2/ws_fossbot/install/setup.bash" >> ~/.bashrc

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
