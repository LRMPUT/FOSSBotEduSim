from setuptools import setup

package_name = 'fossbot_educational_sim_hw'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='author',
    maintainer_email='todo@todo.com',
    description='Motor enable and e-stop services for the simulated FOSSBot',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sim_hw_node = fossbot_educational_sim_hw.sim_hw_node:main',
        ],
    },
)
