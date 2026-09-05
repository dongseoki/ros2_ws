#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int64


class NumberPublisher(Node):
    def __init__(self):
        super().__init__("number_publisher")
        self.declare_parameter("number", 2)
        self.declare_parameter("timer_period", 1.0)
        self.number_ = self.get_parameter("number").value
        self.timer_period_ = self.get_parameter("timer_period").get_parameter_value().double_value
        self.publisher_ = self.create_publisher(Int64, "number", 10)
        self.timer = self.create_timer(self.timer_period_, self.timer_callback)
        self.get_logger().info("Number Publisher node has been started.")


    def timer_callback(self):
        self.publish_number(self.number_)


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