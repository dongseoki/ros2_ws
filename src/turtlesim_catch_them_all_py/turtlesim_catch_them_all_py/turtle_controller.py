#!/usr/bin/env python3
import math
import time

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


POSE_TIMEOUT = 5.0
MOVEMENT_TIMEOUT = 3.0
POSITION_TOLERANCE = 0.1
HEADING_TOLERANCE = 0.2
CONTROL_PERIOD = 0.01
MAX_LINEAR_SPEED = 12.0
MAX_ANGULAR_SPEED = 8.0
LINEAR_GAIN = 7.0
ANGULAR_GAIN = 8.0


class TurtleControllerNode(Node):
    """Drive a turtlesim turtle toward alternating target positions."""

    def __init__(self):
        super().__init__('turtle_controller')
        self.get_logger().info(f'{self.get_name()} begin')
        self.current_pose = None
        self.target_turtle_idx = 0
        time.sleep(5)

        while True:
            self.get_logger().info('try to get_close_turtle')
            kill_target_turtle = self.get_close_turtle()
            self.get_logger().info(
                f'try to go to target turtle {kill_target_turtle[0]} close')
            result = self.move_turtle(
                'turtle1', kill_target_turtle[1], kill_target_turtle[2])
            self.get_logger().info(f'move_turtle result: {result}')
            self.get_logger().info('try to remove turtle')
            self.kill_turtle(kill_target_turtle[0])

    def kill_turtle(self, name):
        pass

    def get_close_turtle(self):
        turtle_pos = [('asdf', 1.0, 1.0), ('zxcv', 10.0, 10.0)]
        target_idx = self.target_turtle_idx
        self.target_turtle_idx = 1 - self.target_turtle_idx
        return turtle_pos[target_idx]

    def pose_callback(self, msg):
        self.current_pose = msg

    def move_turtle(self, turtle_name, x_pos, y_pos):
        self.current_pose = None
        pose_sub = None
        cmd_pub = None
        try:
            pose_sub = self.create_subscription(
                Pose, f'/{turtle_name}/pose', self.pose_callback, 10)
            cmd_pub = self.create_publisher(Twist, f'/{turtle_name}/cmd_vel', 10)

            pose_deadline = time.monotonic() + POSE_TIMEOUT
            while rclpy.ok() and self.current_pose is None:
                remaining = pose_deadline - time.monotonic()
                if remaining <= 0.0:
                    return False
                rclpy.spin_once(self, timeout_sec=min(0.05, remaining))

            if self.current_pose is None:
                return False

            movement_deadline = time.monotonic() + MOVEMENT_TIMEOUT
            while rclpy.ok():
                remaining = movement_deadline - time.monotonic()
                if remaining <= 0.0:
                    return False

                dx = x_pos - self.current_pose.x
                dy = y_pos - self.current_pose.y
                distance = math.hypot(dx, dy)

                if distance < POSITION_TOLERANCE:
                    return True

                target_yaw = math.atan2(dy, dx)
                yaw_error = _normalize_angle(target_yaw - self.current_pose.theta)
                cmd_pub.publish(_compute_velocity_command(distance, yaw_error))
                rclpy.spin_once(self, timeout_sec=min(CONTROL_PERIOD, remaining))

            return False
        finally:
            try:
                if cmd_pub is not None:
                    cmd_pub.publish(Twist())
            finally:
                try:
                    if pose_sub is not None:
                        self.destroy_subscription(pose_sub)
                finally:
                    if cmd_pub is not None:
                        self.destroy_publisher(cmd_pub)


def _compute_velocity_command(distance, yaw_error):
    cmd = Twist()
    if abs(yaw_error) > HEADING_TOLERANCE:
        cmd.angular.z = max(
            -MAX_ANGULAR_SPEED,
            min(MAX_ANGULAR_SPEED, ANGULAR_GAIN * yaw_error))
    else:
        cmd.linear.x = min(MAX_LINEAR_SPEED, LINEAR_GAIN * distance)
    return cmd


def _normalize_angle(angle):
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
