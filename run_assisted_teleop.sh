#!/bin/bash
# Drive the FOSSBot yourself - Nav2's assisted teleop won't let you crash.
# Starts sim + Nav2 + RViz, keeps the assisted-teleop behavior active, and drives
# it from the keyboard via /cmd_vel_teleop. Ctrl+C to stop. Usage: bash run_assisted_teleop.sh
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
    --gpus 'all,"capabilities=compute,utility,graphics"' \
    --env="XAUTHORITY=$XAUTH" \
    --volume="$XAUTH:$XAUTH" \
    --env="NVIDIA_VISIBLE_DEVICES=all" \
    --env="NVIDIA_DRIVER_CAPABILITIES=all" \
    --env="__NV_PRIME_RENDER_OFFLOAD=1" \
    --env="__GLX_VENDOR_LIBRARY_NAME=nvidia" \
    --env="__EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json" \
    --env="__VK_LAYER_NV_optimus=NVIDIA_only" \
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
cleanup(){ [ "$_cleaned" = 1 ] && return; _cleaned=1; kill $(jobs -p) 2>/dev/null; pkill -f "gz sim" 2>/dev/null; pkill -f assisted_teleop 2>/dev/null; }
trap cleanup INT TERM EXIT

ros2 launch fossbot_educational_description single.launch.py world:=depot.sdf rviz:=false x:=-7.51 y:=3.27 yaw:=1.5708 >/tmp/sim.log 2>&1 &
ros2 launch fossbot_educational_navigation navigation.launch.py use_sim_time:=true >/tmp/nav2.log 2>&1 &
rviz2 -d $PKG/config/nav2_default_view.rviz --ros-args -p use_sim_time:=true >/tmp/rviz.log 2>&1 &

echo "Waiting for Nav2..."
n=0
until ros2 action list 2>/dev/null | grep -q /assisted_teleop || [ $n -ge 90 ]; do sleep 1; n=$((n+1)); done
sleep 5

# set the robot's start pose on the map so it shows up localized in the depot
ros2 topic pub -t 3 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
  "{header: {frame_id: map}, pose: {pose: {position: {x: 0.49, y: 3.27, z: 0.0}, orientation: {z: 0.7071, w: 0.7071}}, covariance: [0.25,0,0,0,0,0, 0,0.25,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0.0685]}}" >/dev/null 2>&1

# Keep the assisted-teleop behavior armed (re-send when it times out or aborts).
( while true; do ros2 action send_goal /assisted_teleop nav2_msgs/action/AssistedTeleop "{time_allowance: {sec: 60}}" >/dev/null 2>&1; sleep 0.3; done ) &

echo "Assisted teleop active. Drive: i=forward, ,=back, j/l=turn, k=stop. Ctrl+C to quit."
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel_teleop
INNER
)"
