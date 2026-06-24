#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    parameters = [{
        'frame_id':        'simple_drone/base_link',
        'odom_frame_id':   'simple_drone/odom',
        'map_frame_id':    'map',

        'use_sim_time': True,

        'subscribe_depth':      True,
        'subscribe_rgb':        True,
        'subscribe_rgbd':       False,
        'subscribe_scan':       False,
        'subscribe_scan_cloud': False,

        'approx_sync':        True,
        'sync_queue_size':    50,
        'wait_for_transform': 0.3,

        'Reg/Force3DoF': 'false',
        'Reg/Strategy':  '0',

        'Vis/MinInliers':       '10',
        'Vis/MaxFeatures':      '2000',
        'Vis/FeatureType':      '8',

        'RGBD/NeighborLinkRefining': 'true',
        'RGBD/OptimizeFromGraphEnd': 'false',
        'RGBD/AngularUpdate':   '0.1',
        'RGBD/LinearUpdate':    '0.1',

        'Rtabmap/DetectionRate': '1',
        'Kp/MaxFeatures':       '400',

        'Grid/FromDepth':           'true',
        'Grid/3D':                  'true',
        'Grid/MaxObstacleHeight':   '2.5',
        'Grid/MinGroundHeight':     '-0.3',
        'Grid/MaxGroundHeight':     '0.2',
        'Grid/RangeMax':            '8.0',
        'Grid/CellSize':            '0.05',

        'map_always_update':        True,
        'map_empty_ray_tracing':    True,
    }]

    remappings = [
        ('rgb/image',       '/simple_drone/front/image_raw'),
        ('rgb/camera_info', '/simple_drone/front/camera_info'),
        ('depth/image',     '/simple_drone/front/depth/image_raw'),
        ('odom',            '/simple_drone/odom'),
    ]

    return LaunchDescription([
        Node(
            package='rtabmap_slam',
            executable='rtabmap',
            name='rtabmap',
            output='screen',
            parameters=parameters,
            remappings=remappings,
            arguments=['-d'],
        ),

        Node(
            package='rtabmap_viz',
            executable='rtabmap_viz',
            name='rtabmap_viz',
            output='screen',
            parameters=parameters,
            remappings=remappings,
        ),
    ])