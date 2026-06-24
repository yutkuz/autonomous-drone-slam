import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg = get_package_share_directory('sjtu_drone_bringup')
    config = os.path.join(pkg, 'config', 'cartographer', 'drone_2d.lua')
    config_dir = os.path.join(pkg, 'config', 'cartographer')

    return LaunchDescription([
        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            output='screen',
            arguments=[
                '-configuration_directory', config_dir,
                '-configuration_basename', 'drone_2d.lua'
            ],
            remappings=[
                ('scan', '/simple_drone/lidar/scan'),
                ('imu', '/simple_drone/imu/out'),
            ]
        ),
        Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            name='cartographer_occupancy_grid_node',
            output='screen',
            arguments=['-resolution', '0.05'],
        ),
    ])