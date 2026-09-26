#!/usr/bin/env python3
import rclpy
from rclpy.node import Node


class TurtleControllerNode(Node):  
    def __init__(self):
        super().__init__("turtle_controller")  
        self.get_logger().info(f"{self.get_name()} begin")

def move_turtle(turtle_name, x_pos, y_pos):
    # 1 get turtle_name pos by turtle sim topic

    # x,y 좌표까지 움직일수 있도록 아래에 로직을 작성한다.
    # 아래 명령어 참고. 아래 명령어의 토픽에 메시지 발행하는 방식으로 작업한다.
    # ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
    # "{linear: {x: 2.0}, angular: {z: 1.0}}"

    # 거북이가 x,y좌표까지 움직이면 함수를 true를 리턴한다. 에러 발생시 false를 리턴한다.
    pass

def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode()  
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()