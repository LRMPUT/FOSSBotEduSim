import os
import xacro
from glob import glob
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import (DeclareLaunchArgument, ExecuteProcess, LogInfo, RegisterEventHandler, TimerAction, SetEnvironmentVariable)
from launch.event_handlers import OnProcessStart
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.conditions import IfCondition


def generate_launch_description():
    # Get the package path for 'fossbot_educational_description'
    pkg_pathfinder = get_package_share_directory('fossbot_educational_description')
    
    # Define the path to the URDF file using xacro
    xacro_file = os.path.join(pkg_pathfinder, 'urdf', 'fossbot_educational_gazebo.xacro')
    urdf = xacro.process_file(xacro_file)

    # # Node: joint_state_publisher
    # joint_state_publisher_node = Node(
    #     package='joint_state_publisher',
    #     executable='joint_state_publisher',
    #     output='screen',
    #     parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    # )

    # Node: robot_state_publisher
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': urdf.toxml()},
            {'use_sim_time': LaunchConfiguration('use_sim_time')},  # Enable sim time for rsp_node
        ]
    )

    # World
    world_default = os.path.join(pkg_pathfinder, 'worlds', 'empty.world')

    world_arg = DeclareLaunchArgument(
        'world',
        default_value=world_default,
        description='Path to world file (full path or filename in worlds/ directory)'
    )

    # Set GAZEBO_MODEL_PATH environment variable to include the models directory
    set_gz_resource = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=':'.join([
            os.path.join(pkg_pathfinder),               # contains models/ and worlds/
            os.path.join(pkg_pathfinder, 'worlds')
        ])
    )

    # Gazebo Sim
    world_path = PathJoinSubstitution([
        pkg_pathfinder, 'worlds', LaunchConfiguration('world')
    ])

    start_gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_path],
        output='screen'
    )
 
    # Spawner node to add the robot to the simulation
    spawn_entity_node = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description',   # The robot description is published by the rsp node on the /robot_description topic
                    '-entity', 'fossbot_robot',
                        '-x', LaunchConfiguration('x'),
                        '-y', LaunchConfiguration('y'),
                        '-z', '0.1',                    # Set the initial z position
                        '-R', '0.0',                    # Set the initial roll (rotation about x-axis)
                        '-P', '0.0',                    # Set the initial pitch (rotation about y-axis)
                        '-Y', LaunchConfiguration('yaw')]

    )

    # ROS-Gazebo bridge node to connect ROS 2 topics with Gazebo topics
    bridge_config = os.path.join(pkg_pathfinder, 'config', 'ros_gz_bridge.yaml')

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        parameters=[{'config_file': bridge_config}],
        # arguments=['--ros-args', '-p', f'config_file:={bridge_config}'],
    )


    # Path to RViz configuration file
    rviz_config_file = os.path.join(pkg_pathfinder, 'config', 'display.rviz')

    # Node: rviz2 for visualization
    rviz2_node = Node(
                package='rviz2',
                executable='rviz2',
                output="screen",
                arguments=['-d', rviz_config_file],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                condition=IfCondition(LaunchConfiguration('rviz'))
    )

    # Define and return the LaunchDescription
    return LaunchDescription([
        world_arg,
        set_gz_resource,
        DeclareLaunchArgument(
          'use_sim_time',
          default_value='true',
          description='Use simulation/Gazebo clock'
        ),
        DeclareLaunchArgument(
          'rviz',
          default_value='true',
          description='Start RViz2 (set rviz:=false to use a separate RViz, e.g. nav2)'
        ),
        DeclareLaunchArgument('x', default_value='0.0', description='Spawn x in the gz world'),
        DeclareLaunchArgument('y', default_value='0.0', description='Spawn y in the gz world'),
        DeclareLaunchArgument('yaw', default_value='0.0', description='Spawn yaw in radians'),
        rsp_node,
        start_gazebo,
        spawn_entity_node,
        rviz2_node,
        ros_gz_bridge
    ])
