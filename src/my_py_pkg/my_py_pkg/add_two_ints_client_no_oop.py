#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts




def main(args=None):
    rclpy.init(args=args)
    node = Node("add_two_ints_client_no_oop")

    client = node.create_client(AddTwoInts, "add_two_ints")

    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info("service not available, waiting again...")

    request = AddTwoInts.Request()
    request.a = 2
    request.b = 3
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)
    node.get_logger().info(f"Result of add_two_ints: {future.result().sum}")

    rclpy.shutdown()


if __name__ == "__main__":
    main()