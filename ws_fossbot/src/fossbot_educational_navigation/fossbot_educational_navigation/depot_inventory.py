#!/usr/bin/env python3
"""Autonomous depot inventory round with nav2_simple_commander.

    ros2 run fossbot_educational_navigation depot_inventory
"""
import math
import time

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.qos import QoSProfile, QoSDurabilityPolicy
from visualization_msgs.msg import Marker, MarkerArray

# (name, x, y, yaw) in the map frame
DOCK = ("dock", 0.49, 3.27, 1.5708)
STATIONS = [
    ("station A", 8.0, -1.3, -1.57),
    ("station B", 11.0, -1.3, -1.57),
    ("station C", 14.0, -1.3, -1.57),
]
LEG_TIMEOUT = 90.0


def make_pose(nav, x, y, yaw):
    pose = PoseStamped()
    pose.header.frame_id = "map"
    pose.header.stamp = nav.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def publish_stations(node, stations):
    latched = QoSProfile(depth=1)
    latched.durability = QoSDurabilityPolicy.TRANSIENT_LOCAL
    pub = node.create_publisher(MarkerArray, "inventory_stations", latched)
    stamp = node.get_clock().now().to_msg()
    markers = MarkerArray()
    for i, (name, x, y, yaw) in enumerate(stations):
        arrow = Marker()
        arrow.header.frame_id = "map"
        arrow.header.stamp = stamp
        arrow.ns = "stations"
        arrow.id = i
        arrow.type = Marker.ARROW
        arrow.action = Marker.ADD
        arrow.pose.position.x = float(x)
        arrow.pose.position.y = float(y)
        arrow.pose.orientation.z = math.sin(yaw / 2.0)
        arrow.pose.orientation.w = math.cos(yaw / 2.0)
        arrow.scale.x, arrow.scale.y, arrow.scale.z = 0.5, 0.1, 0.1
        arrow.color.a = 1.0
        if i == 0:
            arrow.color.b = 1.0
        else:
            arrow.color.r, arrow.color.g = 1.0, 0.6
        markers.markers.append(arrow)

        label = Marker()
        label.header.frame_id = "map"
        label.header.stamp = stamp
        label.ns = "labels"
        label.id = i
        label.type = Marker.TEXT_VIEW_FACING
        label.action = Marker.ADD
        label.pose.position.x = float(x)
        label.pose.position.y = float(y)
        label.pose.position.z = 0.4
        label.scale.z = 0.3
        label.color.a = 1.0
        label.text = name
        markers.markers.append(label)
    pub.publish(markers)
    return pub


def drive_to(nav, name, x, y, yaw):
    print(f"-> heading to {name} ({x}, {y})")
    nav.goToPose(make_pose(nav, x, y, yaw))
    start = time.time()
    last = 0.0
    while not nav.isTaskComplete():
        feedback = nav.getFeedback()
        if feedback and time.time() - last > 5.0:
            last = time.time()
            eta = feedback.estimated_time_remaining.sec
            print(f"   {name}: {feedback.distance_remaining:.1f} m to go, ETA {eta} s")
        if time.time() - start > LEG_TIMEOUT:
            nav.cancelTask()
            print(f"   {name}: timed out, skipping")
            break
    return nav.getResult()


def main():
    rclpy.init()
    nav = BasicNavigator()
    print("Waiting for Nav2 to come up...")
    nav.waitUntilNav2Active()

    all_stations = [DOCK] + STATIONS
    station_markers = publish_stations(nav, all_stations)

    report = []
    for name, x, y, yaw in STATIONS:
        result = drive_to(nav, name, x, y, yaw)
        report.append((name, result == TaskResult.SUCCEEDED))

    print("\n===== inventory round report =====")
    for name, scanned in report:
        print(f"  {name}: {'scanned' if scanned else 'MISSED'}")
    done = sum(scanned for _, scanned in report)
    print(f"  {done}/{len(report)} stations scanned")

    rclpy.shutdown()


if __name__ == "__main__":
    main()
