import asyncio

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from my_robot_interfaces.action import Count


class CountActionServer(Node):

    def __init__(self):
        super().__init__('count_action_server')

        self._action_server = ActionServer(
            self,
            Count,
            'count',
            self.execute_callback
        )

    async def execute_callback(self, goal_handle):
        self.get_logger().info(
            f'Goal received: {goal_handle.request.target}'
        )

        feedback_msg = Count.Feedback()

        for i in range(1, goal_handle.request.target + 1):
            await asyncio.sleep(1)

            feedback_msg.current = i
            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(f'Progress: {i}')

        goal_handle.succeed()

        result = Count.Result()
        result.result = goal_handle.request.target

        return result


def main():
    rclpy.init()

    node = CountActionServer()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()