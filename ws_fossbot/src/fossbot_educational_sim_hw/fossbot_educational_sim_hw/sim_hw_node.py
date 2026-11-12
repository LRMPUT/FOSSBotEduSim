"""
Motor enable and e-stop for the simulated FOSSBot.

Mirrors how the real robot handles /cmd_vel behind fossbot-ros2-bridge
(https://github.com/LRMPUT/fossbot-ros2-bridge): the last command is kept and
resent at a fixed rate, and it only reaches the wheels while the motors are
enabled and the e-stop is released.
"""

from geometry_msgs.msg import Twist
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from std_srvs.srv import SetBool


class SimHardware(Node):

    def __init__(self, **kwargs):
        super().__init__('fossbot_sim_hw', **kwargs)

        self.declare_parameter('motors_enabled_on_start', True)
        self.declare_parameter('cmd_rate_hz', 50.0)
        self.declare_parameter('output_topic', '/fossbot_sim/cmd_vel')

        self.motors_enabled = self.get_parameter(
            'motors_enabled_on_start').value
        self.estop = False
        self.last_cmd = Twist()

        output_topic = self.get_parameter('output_topic').value
        self.wheel_pub = self.create_publisher(Twist, output_topic, 10)
        self.create_subscription(Twist, '/cmd_vel', self.on_cmd_vel, 10)

        self.create_service(
            SetBool, '/fossbot/enable_motors', self.on_enable_motors)
        self.create_service(SetBool, '/fossbot/estop', self.on_estop)

        cmd_rate_hz = self.get_parameter('cmd_rate_hz').value
        self.create_timer(1.0 / cmd_rate_hz, self.send_command)

        self.get_logger().info(
            f'motors_enabled={self.motors_enabled}, '
            f'forwarding /cmd_vel to {output_topic}')

    @property
    def can_drive(self):
        return self.motors_enabled and not self.estop

    def on_cmd_vel(self, msg):
        self.last_cmd = msg

    def send_command(self):
        # Like on the real robot, a disabled or e-stopped base still remembers
        # the last command and resumes it once released.
        self.wheel_pub.publish(self.last_cmd if self.can_drive else Twist())

    def on_enable_motors(self, request, response):
        self.motors_enabled = request.data
        self.send_command()
        response.success = True
        response.message = f'motors_enabled={self.motors_enabled}'
        return response

    def on_estop(self, request, response):
        self.estop = request.data
        self.send_command()
        response.success = True
        response.message = f'estop={self.estop}'
        return response

    def stop(self):
        self.wheel_pub.publish(Twist())


def main(args=None):
    # Handle Ctrl+C ourselves, so the context is still alive to send a stop.
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = SimHardware()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        # Gazebo keeps driving with the last command it got, so leave it at
        # zero. The real robot's watchdog does the same when the bridge dies.
        if rclpy.ok():
            node.stop()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
