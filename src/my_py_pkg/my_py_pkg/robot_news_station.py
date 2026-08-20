#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.msg import String
# ros2 interface show example_interfaces/msg/String 

class RobotNewsStation(Node):  # MODIFY NAME
    def __init__(self):
        super().__init__("robot_news_station")
        self.robot_name = "R2-D2"
        self.publisher_ = self.create_publisher(String, "robot_news", 10)
        self.timer = self.create_timer(1.0, self.timer_callback)  # 1 second timer
        self.get_logger().info("Robot News Station node has been started.")

    def timer_callback(self):
        self.publish_news(f"Hello, this is {self.robot_name}'s news update!")

    def publish_news(self, news):
        msg = String()
        msg.data = news
        self.publisher_.publish(msg)
        self.get_logger().info(f"Published news: {news}")


def main(args=None):
    rclpy.init(args=args)
    node = RobotNewsStation() 
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()