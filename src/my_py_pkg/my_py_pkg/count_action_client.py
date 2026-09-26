import rclpy

from rclpy.action import ActionClient
from rclpy.node import Node

from my_robot_interfaces.action import Count


class CountActionClient(Node):

    def __init__(self):
        super().__init__('count_action_client')

        self._action_client = ActionClient(
            self,
            Count,
            'count'
        )

    def send_goal(self):
        goal_msg = Count.Goal()
        goal_msg.target = 5

        self._action_client.wait_for_server()

        self.get_logger().info('Sending goal...')

        future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            self.result_callback
        )

    def feedback_callback(self, feedback):
        current = feedback.feedback.current

        self.get_logger().info(
            f'Feedback: {current}'
        )

    def result_callback(self, future):
        result = future.result().result

        self.get_logger().info(
            f'Result: {result}'
        )


def main():
    rclpy.init()

    node = CountActionClient()
    node.send_goal()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()