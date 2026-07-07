#!/usr/bin/env python3
"""TEMPLATE for Task 7.2 - complete the three TODOs so the robot drives to the
latest goal published on /mission_goal.

    ros2 run fossbot_educational_navigation goal_follower
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator


class GoalFollower(Node):
    def __init__(self):
        super().__init__("goal_follower")
        self.latest = None
        self.pending = False
        # TODO 1: subscribe to "mission_goal" (PoseStamped) -> self.on_goal, queue 10

    def on_goal(self, msg):
        # TODO 2: store msg in self.latest and set self.pending = True
        pass


def main():
    rclpy.init()
    nav = BasicNavigator()
    nav.waitUntilNav2Active()

    follower = GoalFollower()
    print("Goal follower ready. Waiting for goals on /mission_goal ...")

    while rclpy.ok():
        rclpy.spin_once(follower, timeout_sec=0.2)
        if follower.pending:
            follower.pending = False
            goal = follower.latest
            print(f"-> new goal ({goal.pose.position.x:.1f}, {goal.pose.position.y:.1f}) - switching")
            # TODO 3: send goal to Nav2 (a new goal preempts the current one)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
