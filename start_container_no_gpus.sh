#!/bin/bash
if [ -z "$SUDO_USER" ]
then
      user=$USER
else
      user=$SUDO_USER
fi

xhost +SI:localuser:$(id -un)
XAUTH=/tmp/.docker.xauth
if [ ! -f $XAUTH ]
then
    xauth_list=$(xauth nlist :0 | sed -e 's/^..../ffff/')
    if [ ! -z "$xauth_list" ]
    then
        echo $xauth_list | xauth -f $XAUTH nmerge -
    else
        touch $XAUTH
    fi
    chmod a+r $XAUTH
fi

# GPU render nodes (/dev/dri/renderD*) belong to the host's 'render' group - the non-root
# container user needs it for hardware-accelerated rendering in Gazebo/RViz
RENDER_GID=$(getent group render | cut -d: -f3)

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
    ${RENDER_GID:+--group-add $RENDER_GID} \
    --env="XAUTHORITY=$XAUTH" \
    --volume="$XAUTH:$XAUTH" \
    --network=host \
    --pid=host \
    --ipc=host \
    ros2_fossbot_edu \
    bash
