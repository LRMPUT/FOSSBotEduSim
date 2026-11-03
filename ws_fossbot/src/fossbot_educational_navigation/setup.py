from setuptools import setup
import os
from glob import glob

package_name = 'fossbot_educational_navigation'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name, package_name + '.solutions'],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'behavior_trees'), glob('behavior_trees/*.xml')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='author',
    maintainer_email='todo@todo.com',
    description='Nav2 configuration, launch and mission scripts for the educational FOSSBot',
    license='MIT',
    entry_points={
        'console_scripts': [
            'depot_inventory = fossbot_educational_navigation.depot_inventory:main',
            'goal_follower = fossbot_educational_navigation.goal_follower:main',
            'random_station_publisher = fossbot_educational_navigation.random_station_publisher:main',
            'depot_inventory_solution = fossbot_educational_navigation.solutions.depot_inventory:main',
            'goal_follower_solution = fossbot_educational_navigation.solutions.goal_follower:main',
        ],
    },
)
