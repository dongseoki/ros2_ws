#!/usr/bin/env python3
import math
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtlesim.msg import Pose


class TurtleControllerNode(Node):
    def __init__(self):
        super().__init__("turtle_controller")
        self.get_logger().info(f"{self.get_name()} begin")
        self.current_pose = None
        self.target_turtle_idx = 0
        time.sleep(5)
        
        while(True):
            self.get_logger().info(f"try to get_close_turtle")
            kill_target_turtle  = self.get_close_turtle()
            self.get_logger().info(f"try to go to target turtle {kill_target_turtle[0]} close")
            result = self.move_turtle("turtle1", kill_target_turtle[1], kill_target_turtle[2])
            self.get_logger().info(f"move_turtle result: {result}")
            self.get_logger().info(f"try to remove turtle")
            self.kill_turtle(kill_target_turtle[0])

    def kill_turtle(self, name):
        pass

    def get_close_turtle(self):
        turtle_pos = [("asdf",5.0, 5.0), ("zxcv", 7.0, 7.0)]
        target_idx = self.target_turtle_idx
        self.target_turtle_idx = 1 - self.target_turtle_idx
        return turtle_pos[target_idx]


    def pose_callback(self, msg):
        self.current_pose = msg

    def move_turtle(self, turtle_name, x_pos, y_pos):
        pose_sub = self.create_subscription(Pose, f"/{turtle_name}/pose", self.pose_callback, 10)
        cmd_pub = self.create_publisher(Twist, f"/{turtle_name}/cmd_vel", 10)

        try:
            start_time = time.monotonic()
            timeout = 5.0

            while rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.05)
                if self.current_pose is not None:
                    break
                if time.monotonic() - start_time > timeout:
                    return False

            tolerance = 0.1
            while rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.05)

                if self.current_pose is None:
                    if time.monotonic() - start_time > timeout:
                        return False
                    continue

                dx = x_pos - self.current_pose.x
                dy = y_pos - self.current_pose.y
                distance = math.hypot(dx, dy)

                if distance < tolerance:
                    cmd_pub.publish(Twist())
                    return True

                target_yaw = math.atan2(dy, dx)
                yaw_error = _normalize_angle(target_yaw - self.current_pose.theta)

                cmd = Twist()
                if abs(yaw_error) > 0.05:
                    cmd.angular.z = max(-2.0, min(2.0, yaw_error * 2.0))
                else:
                    cmd.linear.x = max(0.0, min(2.0, distance))

                cmd_pub.publish(cmd)

            return False
        finally:
            self.destroy_subscription(pose_sub)
            self.destroy_publisher(cmd_pub)


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

if __name__ == "__main__":
    main()