#!/usr/bin/env python3
"""Publish a random station on /mission_goal every few seconds.

    ros2 run fossbot_educational_navigation random_station_publisher
"""
import math
import random
import time

import rclpy
from geometry_msgs.msg import PoseStamped

from fossbot_educational_navigation.depot_inventory import STATIONS

MIN_INTERVAL = 8.0
MAX_INTERVAL = 18.0


def main():
    rclpy.init()
    node = rclpy.create_node("random_station_publisher")
    pub = node.create_publisher(PoseStamped, "mission_goal", 10)
    time.sleep(1.0)

    last = None
    while rclpy.ok():
        station = random.choice([s for s in STATIONS if s != last] or STATIONS)
        last = station
        name, x, y, yaw = station
        msg = PoseStamped()
        msg.header.frame_id = "map"
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.pose.position.x = float(x)
        msg.pose.position.y = float(y)
        msg.pose.orientation.z = math.sin(yaw / 2.0)
        msg.pose.orientation.w = math.cos(yaw / 2.0)
        pub.publish(msg)
        wait = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
        print(f"published {name} ({x}, {y}); next in {wait:.0f} s")
        time.sleep(wait)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
