from setuptools import setup
import os
from glob import glob

package_name = 'fossbot_educational_description'

data_files = [
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
    (os.path.join('share', package_name, 'config'), glob('config/*')),
    (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
    (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
    (os.path.join('share', package_name, 'worlds', 'objects'), glob('worlds/objects/*.stl')),
]

for path, _, files in os.walk('meshes'):
    if files:
        install_dir = os.path.join('share', package_name, path)
        data_files.append((install_dir, [os.path.join(path, f) for f in files]))

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='author',
    maintainer_email='todo@todo.com',
    description='The ' + package_name + ' package',
    license='MIT',
    entry_points={
        'console_scripts': [
            'random_spawner = fossbot_educational_description.random_spawner:main',
        ],
    },
)
