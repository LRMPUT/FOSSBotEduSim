# FossBot Educational Version

- [FossBot Educational Version](#fossbot-educational-version)
  - [Workspace preparation](#workspace-preparation)
    - [Clone the repository](#clone-the-repository)
      - [TODO: Add the repository link](#todo-add-the-repository-link)
    - [Docker](#docker)
      - [Build the image](#build-the-image)
      - [Start the container](#start-the-container)
      - [Join a running container](#join-a-running-container)
    - [Native Installation](#native-installation)
      - [TODO: VERIFY THE STEPS FOR NATIVE INSTALLATION](#todo-verify-the-steps-for-native-installation)
      - [Requirements](#requirements)
      - [Installation](#installation)
  - [Quick Start](#quick-start)
    - [Teleop](#teleop)
    - [SLAM Toolbox](#slam-toolbox)
    - [Navigation](#navigation)
  - [Issues](#issues)
  - [Acknowledgements](#acknowledgements)
  - [TODO: Add Acknowledgements](#todo-add-acknowledgements)

## Workspace preparation

### Clone the repository

#### TODO: Add the repository link

```bash
git clone <repository_link>
```

### Docker

You can use the provided Dockerfile to build an image with all the dependencies installed. This is the recommended way to run the simulation, as it ensures that all the dependencies are correctly installed and configured.

The container is configured to use the host's GPU and display, so you can run the simulation with hardware acceleration and visualize it on your screen. 

The [ws_fossbot](ws_fossbot) directory is mounted as a volume in the container, so any changes you make to the code will be reflected in the container (and vice versa).

#### Build the image
```bash
bash build_image.sh
```

#### Start the container
```bash
bash start_container.sh
```

#### Join a running container
```bash
docker exec -it ros2_fossbot_edu bash
```

### Native Installation

You can also run the simulation natively on your machine. 

#### TODO: VERIFY THE STEPS FOR NATIVE INSTALLATION

#### Requirements
- ROS2 Jazzy
- Ubuntu 24.04


#### Installation
    
```bash
sudo apt update
sudo apt upgrade

cd fossbot_industrial_ros2
cd ws_fossbot
cd src 
git clone https://github.com/SICKAG/sick_safetyscanners2.git
cd ..
source /opt/ros/jazzy/setup.bash
# Install dependencies
sudo apt-get install ros-jazzy-sick-safetyscanners2 ros-jazzy-sick-safetyscanners2-interfaces
sudo apt-get install ros-jazzy-joint-state-publisher
sudo apt-get install ros-jazzy-sick-safetyscanners-base
sudo apt install ros-jazzy-librealsense2
sudo apt install ros-jazzy-realsense2-description 
sudo apt install ros-jazzy-realsense2-camera
sudo apt install ros-jazzy-ros2-controllers
sudo apt install ros-jazzy-ros2-control
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup
sudo apt install ros-jazzy-slam-toolbox
sudo apt install ros-jazzy-teleop-twist-keyboard
sudo apt install ros-jazzy-gazebo-ros-pkgs
sudo apt install ros-jazzy-twist-mux
sudo apt install ros-jazzy-ros-gz ros-jazzy-ros-gz-sim ros-jazzy-ros-gz-bridge

# Build the workspace
colcon build
source install/setup.bash
```

## Quick Start

Run:
```bash
ros2 launch fossbot_educational_description single.launch.py world:=simple_shapes.sdf
```

### Teleop

Control the robot using the keyboard from the terminal

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### SLAM Toolbox

Build the map using the data from lidar and odometry

```bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=True
```

### Navigation

Set the goal pose in map from RViz2

```bash
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=True params_file:=/fossbot_ros2/ws_fossbot/src/fossbot_educational_description/config/nav2_params.yaml
```

![FossBot Educational Map and Navigation](assets/fossbot_edu_planning.gif)

## Issues

If you encounter any issues, please report them in the Issues section of the repository.

## Acknowledgements

## TODO: Add Acknowledgements