#!/usr/bin/env python3
# Final benchmark: RTAB-Map with lidar and side depth point clouds.
# Side depth point clouds are merged with lidar before RTAB-Map consumes them.

import os
from pathlib import Path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

THIS_DIR = os.path.dirname(os.path.realpath(__file__))


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    qos = LaunchConfiguration('qos')
    rtabmapviz = LaunchConfiguration('rtabmapviz')

    # Store the RTAB-Map database under this experiment's output folder.
    final_db = str(Path.home() / "Desktop/Project-Final/final-benchmark-experiment/outputs/rtabmap.db")
    os.makedirs(str(Path.home() / "Desktop/Project-Final/final-benchmark-experiment/outputs"), exist_ok=True)

    rtabmap_params = {
        'database_path': final_db,
        'frame_id': 'simple_drone/base_link',
        'use_sim_time': use_sim_time,
        'approx_sync': True,
        'sync_queue_size': 30,
        'topic_queue_size': 30,
        'wait_for_transform': 0.5,
        'Rtabmap/DetectionRate': '0.35',
        'subscribe_rgbd': True,
        'subscribe_scan_cloud': True,
        'subscribe_depth': False,
        'subscribe_rgb': False,
        'subscribe_odom_info': False,
        'qos': qos,
        'qos_scan': qos,
        'qos_image': qos,
        'qos_camera_info': qos,
        'Reg/Strategy': '1',
        'Vis/MinInliers': '12',
        'Vis/MaxFeatures': '500',
        'RGBD/NeighborLinkRefining': 'true',
        'RGBD/ProximityBySpace': 'true',
        'RGBD/AngularUpdate': '0.10',
        'RGBD/LinearUpdate': '0.10',
        'RGBD/OptimizeFromGraphEnd': 'false',
        'RGBD/OptimizeMaxError': '6.0',
        'Mem/UseOdomGravity': 'true',
        'Mem/NotLinkedNodesKept': 'false',
        'Mem/STMSize': '30',
        'Mem/DepthCompressionFormat': '.png',
        'Optimizer/Strategy': '1',
        'Optimizer/Iterations': '60',
        'Grid/Sensor': '2',
        'Grid/3D': 'true',
        'Grid/RayTracing': 'true',
        'Grid/RangeMax': '8.0',
        'Grid/CellSize': '0.04',
        'Grid/NormalsSegmentation': 'false',
        'Grid/MaxGroundHeight': '0.1',
        'Icp/MaxCorrespondenceDistance': '0.08',
        'Icp/PointToPlane': 'true',
        'Icp/Iterations': '30',
        'cloud_noise_filtering_radius': '0.05',
        'cloud_noise_filtering_min_neighbors': '3',
    }

    # ---- Duzelticiler (entegre) ----
    odom_fixer = ExecuteProcess(
        cmd=['python3', os.path.join(THIS_DIR, 'odom_frame_fixer.py'),
             '--ros-args', '-p', 'publish_tf:=false'],
        output='screen',
    )
    camera_fixer = ExecuteProcess(
        cmd=['python3', os.path.join(THIS_DIR, 'camera_frame_fixer.py')],
        output='screen',
    )
    cloud_merger = ExecuteProcess(
        cmd=['python3', str(Path.home() / 'Desktop/Project-Final/final-benchmark-experiment/scripts/merge_side_depth_clouds.py')],
        output='screen',
    )

    # ---- Optik frame'ler ----
    front_optical_tf = Node(
        package='tf2_ros', executable='static_transform_publisher',
        name='front_cam_optical_tf', output='screen',
        arguments=[
            '--x', '0', '--y', '0', '--z', '0',
            '--qx', '-0.5', '--qy', '0.5', '--qz', '-0.5', '--qw', '0.5',
            '--frame-id', 'simple_drone/front_cam_link',
            '--child-frame-id', 'simple_drone/front_cam_optical',
        ],
        parameters=[{'use_sim_time': use_sim_time}],
    )
    right_optical_tf = Node(
        package='tf2_ros', executable='static_transform_publisher',
        name='right_cam_optical_tf', output='screen',
        arguments=[
            '--x', '0', '--y', '0', '--z', '0',
            '--qx', '-0.5', '--qy', '0.5', '--qz', '-0.5', '--qw', '0.5',
            '--frame-id', 'simple_drone/right_cam_link',
            '--child-frame-id', 'simple_drone/right_cam_optical',
        ],
        parameters=[{'use_sim_time': use_sim_time}],
    )
    left_optical_tf = Node(
        package='tf2_ros', executable='static_transform_publisher',
        name='left_cam_optical_tf', output='screen',
        arguments=[
            '--x', '0', '--y', '0', '--z', '0',
            '--qx', '-0.5', '--qy', '0.5', '--qz', '-0.5', '--qw', '0.5',
            '--frame-id', 'simple_drone/left_cam_link',
            '--child-frame-id', 'simple_drone/left_cam_optical',
        ],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    front_rgbd_sync = Node(
        package='rtabmap_sync', executable='rgbd_sync', name='front_rgbd_sync', output='screen',
        parameters=[{'approx_sync': True, 'use_sim_time': use_sim_time, 'qos': qos}],
        remappings=[
            ('rgb/image',       '/simple_drone/front/image_optical'),
            ('depth/image',     '/simple_drone/front/depth/image_optical'),
            ('rgb/camera_info', '/simple_drone/front/camera_info_optical'),
            ('rgbd_image',      '/rgbd_image_front'),
        ],
    )
    rtabmap = Node(
        package='rtabmap_slam', executable='rtabmap', output='screen',
        parameters=[rtabmap_params],
        remappings=[
            ('rgbd_image', '/rgbd_image_front'),
            ('scan_cloud', '/final_benchmark/merged_scan_cloud'),
            ('odom',       '/simple_drone/odom_fixed'),
        ],
        arguments=['-d'],
    )

    rtabmap_viz = Node(
        package='rtabmap_viz', executable='rtabmap_viz', output='screen',
        condition=IfCondition(rtabmapviz),
        parameters=[rtabmap_params],
        remappings=[
            ('rgbd_image', '/rgbd_image_front'),
            ('scan_cloud', '/final_benchmark/merged_scan_cloud'),
            ('odom',       '/simple_drone/odom_fixed'),
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('qos', default_value='1'),
        DeclareLaunchArgument('rtabmapviz', default_value='false'),
        odom_fixer,
        camera_fixer,
        cloud_merger,
        front_optical_tf,
        right_optical_tf,
        left_optical_tf,
        front_rgbd_sync,
        rtabmap,
        rtabmap_viz,
    ])
