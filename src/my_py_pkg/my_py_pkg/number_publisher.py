#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int64


class NumberPublisher(Node):
    def __init__(self):
        super().__init__("number_publisher")
        self.publisher_ = self.create_publisher(Int64, "number", 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.get_logger().info("Number Publisher node has been started.")


    def timer_callback(self):
        self.publish_number(2)


    def publish_number(self, number):
        msg = Int64()
        msg.data = number
        self.publisher_.publish(msg)
        self.get_logger().info(f"Published number: {msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = NumberPublisher()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()