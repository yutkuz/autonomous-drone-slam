#!/usr/bin/env python3
# Copyright 2023 Georg Novotny
#
# Licensed under the GNU GENERAL PUBLIC LICENSE, Version 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.gnu.org/licenses/gpl-3.0.en.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -*- coding: utf-8 -*-
import os
import sys
import rclpy
import math  
from gazebo_msgs.srv import SpawnEntity


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node('spawn_drone')
    cli = node.create_client(SpawnEntity, '/spawn_entity')

    content = sys.argv[1]
    namespace = sys.argv[2]

    req = SpawnEntity.Request()
    req.name = namespace
    req.xml = content
    req.robot_namespace = namespace
    req.reference_frame = "world"

    req.reference_frame = "world"

    # Maps10 live tests can provide a world-derived spawn position. Defaults
    # keep the old Maps8 behavior for existing maps/scripts.
    req.initial_pose.position.x = float(os.environ.get("MAPS10_SPAWN_X", "-6.2"))
    req.initial_pose.position.y = float(os.environ.get("MAPS10_SPAWN_Y", "-4.6"))
    req.initial_pose.position.z = float(os.environ.get("MAPS10_SPAWN_Z", "0.0"))

    # Yaw açısını quaternion'a çevir (sadece Z ekseni dönüşü)
    yaw = float(os.environ.get("MAPS10_SPAWN_YAW", "0.0"))
    req.initial_pose.orientation.z = math.sin(yaw / 2.0)
    req.initial_pose.orientation.w = math.cos(yaw / 2.0)
    # ────────────────────────────────

    while not cli.wait_for_service(timeout_sec=1.0):
        ...

    while not cli.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('service not available, waiting again...')

    future = cli.call_async(req)
    rclpy.spin_until_future_complete(node, future)

    if future.result() is not None:
        node.get_logger().info(
            'Result ' + str(future.result().success) + " " + future.result().status_message)
    else:
        node.get_logger().info('Service call failed %r' % (future.exception(),))

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
