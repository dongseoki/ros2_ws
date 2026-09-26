#!/usr/bin/env python3
import rclpy
from rclpy.node import Node


class TurtleControllerNode(Node):  
    def __init__(self):
        super().__init__("turtle_controller")  
        self.get_logger().info(f"{self.get_name()} begin")


def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode()  
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()