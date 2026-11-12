import time

from fossbot_educational_sim_hw.sim_hw_node import SimHardware
from geometry_msgs.msg import Twist
import pytest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.parameter import Parameter
from std_srvs.srv import SetBool


OUTPUT_TOPIC = '/test_sim_hw/cmd_vel'


class Harness:
    """Runs the node next to a test client in one executor."""

    def __init__(self, motors_enabled_on_start):
        self.hw = SimHardware(parameter_overrides=[
            Parameter('motors_enabled_on_start', value=motors_enabled_on_start),
            Parameter('output_topic', value=OUTPUT_TOPIC),
        ])

        self.client = rclpy.create_node('test_client')
        self.cmd_pub = self.client.create_publisher(Twist, '/cmd_vel', 10)
        self.received = []
        self.client.create_subscription(
            Twist, OUTPUT_TOPIC, self.received.append, 10)
        self.enable_cli = self.client.create_client(
            SetBool, '/fossbot/enable_motors')
        self.estop_cli = self.client.create_client(SetBool, '/fossbot/estop')

        self.executor = SingleThreadedExecutor()
        self.executor.add_node(self.hw)
        self.executor.add_node(self.client)
        self.spin_for(0.3)  # let discovery settle

    def spin_for(self, seconds):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            self.executor.spin_once(timeout_sec=0.01)

    def wheel_command(self):
        """Return the latest command sent towards Gazebo."""
        self.received.clear()
        self.spin_for(0.2)
        assert self.received, 'nothing was sent towards Gazebo'
        return self.received[-1].linear.x, self.received[-1].angular.z

    def drive(self, linear_x, angular_z=0.0):
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        self.cmd_pub.publish(msg)
        self.spin_for(0.1)

    def call(self, client, value):
        assert client.wait_for_service(timeout_sec=2.0)
        future = client.call_async(SetBool.Request(data=value))
        self.executor.spin_until_future_complete(future, timeout_sec=2.0)
        return future.result()

    def close(self):
        self.executor.shutdown()
        self.hw.destroy_node()
        self.client.destroy_node()


@pytest.fixture
def ros():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def robot(ros):
    harness = Harness(motors_enabled_on_start=True)
    yield harness
    harness.close()


def test_sends_zero_before_any_command(robot):
    assert robot.wheel_command() == (0.0, 0.0)


def test_single_command_is_held(robot):
    robot.drive(0.2, 0.5)
    robot.spin_for(1.0)
    assert robot.wheel_command() == (0.2, 0.5)


def test_zero_twist_stops(robot):
    robot.drive(0.2)
    robot.drive(0.0)
    assert robot.wheel_command() == (0.0, 0.0)


def test_estop_blocks_and_release_resumes(robot):
    robot.drive(0.2)

    response = robot.call(robot.estop_cli, True)
    assert response.success
    assert response.message == 'estop=True'
    assert robot.wheel_command() == (0.0, 0.0)

    robot.drive(0.3)
    assert robot.wheel_command() == (0.0, 0.0)

    robot.call(robot.estop_cli, False)
    assert robot.wheel_command() == (0.3, 0.0)


def test_disabling_motors_stops(robot):
    robot.drive(0.2)

    response = robot.call(robot.enable_cli, False)
    assert response.success
    assert response.message == 'motors_enabled=False'
    assert robot.wheel_command() == (0.0, 0.0)


def test_motors_can_start_disabled(ros):
    robot = Harness(motors_enabled_on_start=False)
    try:
        robot.drive(0.2)
        assert robot.wheel_command() == (0.0, 0.0)

        robot.call(robot.enable_cli, True)
        assert robot.wheel_command() == (0.2, 0.0)
    finally:
        robot.close()


def test_estop_wins_over_enable(robot):
    robot.drive(0.2)
    robot.call(robot.estop_cli, True)
    robot.call(robot.enable_cli, True)
    assert robot.wheel_command() == (0.0, 0.0)
