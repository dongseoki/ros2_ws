#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int64


class NumberCounterNode(Node):
    def __init__(self):
        super().__init__("number_counter")
        self.number_count_ = 0
        self.publisher_ = self.create_publisher(Int64, "number_count", 10)
        self.subscription_ = self.create_subscription(
            Int64,
            "number",
            self.number_callback,
            10,
        )
        self.get_logger().info(
            f"Number counter initialized with: {self.number_count_}"
        )

    def number_callback(self, msg):
        self.number_count_ += msg.data
        self.get_logger().info(f"Updated number count: {self.number_count_}")

        count_msg = Int64()
        count_msg.data = self.number_count_
        self.publisher_.publish(count_msg)


def main(args=None):
    rclpy.init(args=args)
    node = NumberCounterNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()