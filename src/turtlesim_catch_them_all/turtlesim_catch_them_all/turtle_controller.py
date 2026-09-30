#!/usr/bin/env python3
import math
import rclpy
from functools import partial
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from my_robot_interfaces.msg import Turtle
from my_robot_interfaces.msg import TurtleArray
from my_robot_interfaces.srv import CatchTurtle


class TurtleControllerNode(Node):  
    def __init__(self):
        super().__init__("turtle_controller")  

        # parameter
        self.declare_parameter("catch_closest_turtle_first", True)
        self.catch_closest_turtle_first_ = self.get_parameter(
            "catch_closest_turtle_first").value

        # var
        self.turtle_to_catch_: Turtle = None
        self.pose_: Pose = None

        # publisher
        self.cmd_vel_publisher_ = self.create_publisher(
            Twist, "/turtle1/cmd_vel", 10)

        # subscriber
        self.pose_subscriber_ = self.create_subscription(Pose, "/turtle1/pose", self.callback_pose, 10)
        self.alive_turtles_subscriber_ = self.create_subscription(
            TurtleArray, "alive_turtles", self.callback_alive_turtles, 10)

        # client
        self.catch_turtle_client_ = self.create_client(CatchTurtle, "catch_turtle")

        # timer
        self.controll_loop_timer_ = self.create_timer(0.01, self.control_loop)

    def callback_alive_turtles(self, msg: TurtleArray):
        if len(msg.list) > 0:
            if self.catch_closest_turtle_first_:
                closest_turtle = None
                closest_turtle_distance = None

                for turtle in msg.list:
                    dist_x = turtle.pose_x - self.pose_.x
                    dist_y = turtle.pose_y - self.pose_.y
                    distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                    if closest_turtle == None or distance < closest_turtle_distance:
                        closest_turtle = turtle
                        closest_turtle_distance = distance
                self.turtle_to_catch_ = closest_turtle
            else:
                self.turtle_to_catch_ = msg.turtles[0]

    def callback_pose(self, pose: Pose):
        self.pose_ = pose

    def callback_alive_turtles(self, msg: TurtleArray):
        if len(msg.list) > 0:
            self.turtle_to_catch_ = msg.list[0]

    def control_loop(self):
        if self.pose_ == None or self.turtle_to_catch_ == None:
            self.get_logger().info("pose or turtle_to_catch_ is None")
            self.get_logger().info(f"self pose:{self.pose_}, turtle_to_catch_:{self.turtle_to_catch_}")
            return

        dist_x = self.turtle_to_catch_.x_pos - self.pose_.x
        dist_y = self.turtle_to_catch_.y_pos - self.pose_.y
        distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)

        cmd = Twist()

        if distance > 0.5:
            # position
            cmd.linear.x = 2*distance

            # orientation
            goal_theta = math.atan2(dist_y, dist_x)
            diff = goal_theta - self.pose_.theta
            if diff > math.pi:
                diff -= 2*math.pi
            elif diff < -math.pi:
                diff += 2*math.pi
            cmd.angular.z = 6*diff
        else:
            # target reached
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.call_catch_turtle_service(self.turtle_to_catch_.name)
            self.turtle_to_catch_ = None

        self.cmd_vel_publisher_.publish(cmd)

    def call_catch_turtle_service(self, turtle_name):
        while not self.catch_turtle_client_.wait_for_service(1.0):
            self.get_logger().warn("Waiting for catch turtle service...")
        
        request = CatchTurtle.Request()
        request.name = turtle_name

        future = self.catch_turtle_client_.call_async(request)
        future.add_done_callback(
            partial(self.callback_call_catch_turtle_service, turtle_name=turtle_name))

    def callback_call_catch_turtle_service(self, future, turtle_name):
        response: CatchTurtle.Response = future.result()
        if not response.result:
            self.get_logger().error("Turtle " + turtle_name + " could not be removed")    

def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode()  
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()