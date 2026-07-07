import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    pkg_share = get_package_share_directory('fossbot_educational_navigation')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    bt_dir = os.path.join(pkg_share, 'behavior_trees')
    default_map = os.path.join(pkg_share, 'maps', 'map.yaml')

    # inject the BT XML paths from this package's share dir
    configured_params = RewrittenYaml(
        source_file=os.path.join(pkg_share, 'config', 'nav2_params.yaml'),
        param_rewrites={
            'default_nav_to_pose_bt_xml':
                os.path.join(bt_dir, 'navigate_to_pose_w_replanning_and_recovery.xml'),
            'default_nav_through_poses_bt_xml':
                os.path.join(bt_dir, 'navigate_through_poses_w_replanning_and_recovery.xml'),
        },
        convert_types=True,
    )

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
            launch_arguments={
                'map': LaunchConfiguration('map'),
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'slam': 'False',
                'params_file': configured_params,
            }.items(),
        ),
    ])
