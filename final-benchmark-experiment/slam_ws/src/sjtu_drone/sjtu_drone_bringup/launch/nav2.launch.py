#!/usr/bin/env python3
"""
sjtu_drone için Nav2 launch dosyası.
RTAB-Map'in /map çıktısını kullanır, drone'a /simple_drone/cmd_vel ile komut verir.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    
    nav2_yaml = os.path.join(
        get_package_share_directory('sjtu_drone_bringup'),
        'config',
        'nav2_params.yaml'
    )
    
    # Tüm Nav2 node'larının cmd_vel'i drone'a yönlendirsin
    cmd_vel_remap = ('/cmd_vel', '/cmd_vel_nav')
    
    lifecycle_nodes = [
        'planner_server',
        'controller_server',
        'behavior_server',
        'bt_navigator',
        'waypoint_follower',
    ]
    
    return LaunchDescription([
        
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[nav2_yaml],
        ),
        
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[nav2_yaml],
            remappings=[cmd_vel_remap],
        ),
        
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[nav2_yaml],
            remappings=[cmd_vel_remap],
        ),
        
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[nav2_yaml],
        ),
        
        Node(
            package='nav2_waypoint_follower',
            executable='waypoint_follower',
            name='waypoint_follower',
            output='screen',
            parameters=[nav2_yaml],
        ),
        
        # Lifecycle manager — Nav2 node'larını sırayla aktive eder
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'autostart': True,
                'node_names': lifecycle_nodes,
            }],
        ),
    ])
