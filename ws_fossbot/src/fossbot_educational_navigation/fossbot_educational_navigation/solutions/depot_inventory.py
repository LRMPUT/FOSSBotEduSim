#!/usr/bin/env python3
"""Reference solution for Task 7.1 (inventory round with a fourth station and docking).

    ros2 run fossbot_educational_navigation depot_inventory_solution
"""
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

from fossbot_educational_navigation.depot_inventory import (
    DOCK, STATIONS, drive_to, publish_stations)

STATIONS_FULL = STATIONS + [("station D", 17.0, -1.3, -1.57)]


def main():
    rclpy.init()
    nav = BasicNavigator()
    nav.waitUntilNav2Active()

    station_markers = publish_stations(nav, [DOCK] + STATIONS_FULL)

    nav.undockRobot("simple_home_dock")
    while not nav.isTaskComplete():
        pass

    report = []
    for name, x, y, yaw in STATIONS_FULL:
        result = drive_to(nav, name, x, y, yaw)
        report.append((name, result == TaskResult.SUCCEEDED))

    nav.dockRobotByID("home_dock")
    while not nav.isTaskComplete():
        pass

    print("\n===== inventory round report =====")
    for name, scanned in report:
        print(f"  {name}: {'scanned' if scanned else 'MISSED'}")
    done = sum(scanned for _, scanned in report)
    print(f"  {done}/{len(report)} stations scanned, robot back at dock")

    rclpy.shutdown()


if __name__ == "__main__":
    main()
