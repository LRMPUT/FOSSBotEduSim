#!/bin/bash
# Start the container with the simulation, Nav2 and RViz - without NVIDIA GPU passthrough.
# Use this on a workstation with integrated graphics. Usage: bash run_nav_no_gpus.sh   (Ctrl+C to stop)
cd "$(dirname "$0")" || exit 1

xhost +local:root >/dev/null 2>&1
XAUTH=/tmp/.docker.xauth
if [ ! -f "$XAUTH" ]; then
    xauth_list=$(xauth nlist :0 | sed -e 's/^..../ffff/')
    if [ -n "$xauth_list" ]; then echo "$xauth_list" | xauth -f "$XAUTH" nmerge -; else touch "$XAUTH"; fi
    chmod a+r "$XAUTH"
fi

docker rm -f ros2_fossbot_edu >/dev/null 2>&1 || true

docker run -it --rm \
    --name=ros2_fossbot_edu \
    --shm-size=1g \
    --ulimit memlock=-1 \
    --env="DISPLAY=$DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --volume="$(pwd)/ws_fossbot:/fossbot_ros2/ws_fossbot" \
    --device=/dev/dri:/dev/dri \
    --group-add video \
    --env="XAUTHORITY=$XAUTH" \
    --volume="$XAUTH:$XAUTH" \
    --network=host \
    --pid=host \
    --ipc=host \
    ros2_fossbot_edu \
    bash -lc "$(cat <<'INNER'
source /opt/ros/jazzy/setup.bash
source /fossbot_ros2/ws_fossbot/install/setup.bash
WS=/fossbot_ros2/ws_fossbot
PKG=$WS/src/fossbot_educational_navigation

_cleaned=0
cleanup(){ [ "$_cleaned" = 1 ] && return; _cleaned=1; kill $(jobs -p) 2>/dev/null; pkill -f "gz sim" 2>/dev/null; }
trap cleanup INT TERM EXIT

ros2 launch fossbot_educational_description single.launch.py world:=depot.sdf rviz:=false x:=-7.51 y:=3.27 yaw:=1.5708 &
ros2 launch fossbot_educational_navigation navigation.launch.py use_sim_time:=true &
rviz2 -d $PKG/config/nav2_default_view.rviz --ros-args -p use_sim_time:=true &

# set the robot's start pose on the map (depot dock, facing the shelves) once AMCL is up
( until ros2 topic list 2>/dev/null | grep -q /amcl_pose; do sleep 1; done; sleep 2
  ros2 topic pub -t 3 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
    "{header: {frame_id: map}, pose: {pose: {position: {x: 0.49, y: 3.27, z: 0.0}, orientation: {z: 0.7071, w: 0.7071}}, covariance: [0.25,0,0,0,0,0, 0,0.25,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0.0685]}}" >/dev/null 2>&1 ) &
wait
INNER
)"
