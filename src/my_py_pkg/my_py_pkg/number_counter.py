#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.srv import SetBool
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
        self.server_ = self.create_service(
            SetBool, "reset_counter", self.reset_counter_callback
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

    def reset_counter_callback(self, request : SetBool.Request, response : SetBool.Response):
        if request.data:
            self.number_count_ = 0
            self.get_logger().info("Number count has been reset to 0.")
        else:
            self.get_logger().info("Reset request received, but no action taken.")
        response.success = True
        return response

def main(args=None):
    rclpy.init(args=args)
    node = NumberCounterNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()