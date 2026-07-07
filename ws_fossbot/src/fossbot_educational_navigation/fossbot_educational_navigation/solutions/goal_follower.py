#!/usr/bin/env python3
"""Reference solution for Task 7.2 (goal_follower).

    ros2 run fossbot_educational_navigation goal_follower_solution
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
        self.create_subscription(PoseStamped, "mission_goal", self.on_goal, 10)

    def on_goal(self, msg):
        self.latest = msg
        self.pending = True


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
            nav.goToPose(goal)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
