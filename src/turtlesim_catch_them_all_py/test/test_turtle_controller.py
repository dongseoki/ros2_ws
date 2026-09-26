# Copyright 2026
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import math

from turtlesim.msg import Pose

from turtlesim_catch_them_all_py import turtle_controller


class FakePublisher:
    """Collect messages published by a controller call."""

    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append(message)


class FakeController:
    """Provide ROS node operations needed by the movement method."""

    def __init__(self):
        self.current_pose = None
        self.publisher = FakePublisher()
        self.destroyed_subscription = False
        self.destroyed_publisher = False

    def pose_callback(self, message):
        self.current_pose = message

    def create_subscription(self, *_args):
        return object()

    def create_publisher(self, *_args):
        return self.publisher

    def destroy_subscription(self, _subscription):
        self.destroyed_subscription = True

    def destroy_publisher(self, _publisher):
        self.destroyed_publisher = True


def test_velocity_command_turns_before_moving():
    command = turtle_controller._compute_velocity_command(15.6, math.pi)

    assert command.linear.x == 0.0
    assert command.angular.z == turtle_controller.MAX_ANGULAR_SPEED


def test_velocity_command_brakes_near_goal_and_caps_speed():
    fast_command = turtle_controller._compute_velocity_command(15.6, 0.0)
    near_command = turtle_controller._compute_velocity_command(0.2, 0.0)

    assert fast_command.linear.x == turtle_controller.MAX_LINEAR_SPEED
    assert near_command.linear.x < fast_command.linear.x
    assert near_command.linear.x == turtle_controller.LINEAR_GAIN * 0.2


def test_normalize_angle_wraps_across_pi():
    assert math.isclose(
        turtle_controller._normalize_angle(math.pi + 0.1), -math.pi + 0.1)


def test_move_turtle_returns_true_and_stops_at_goal(monkeypatch):
    node = FakeController()
    monkeypatch.setattr(turtle_controller.rclpy, 'ok', lambda: True)

    def spin_once(fake_node, timeout_sec):
        fake_node.current_pose = Pose(x=4.0, y=5.0, theta=0.0)

    monkeypatch.setattr(turtle_controller.rclpy, 'spin_once', spin_once)

    result = turtle_controller.TurtleControllerNode.move_turtle(
        node, 'turtle1', 4.0, 5.0)

    assert result is True
    assert node.publisher.messages[-1].linear.x == 0.0
    assert node.publisher.messages[-1].angular.z == 0.0
    assert node.destroyed_subscription
    assert node.destroyed_publisher


def test_maximum_diagonal_move_finishes_within_deadline(monkeypatch):
    node = FakeController()
    now = [0.0]
    monkeypatch.setattr(turtle_controller.rclpy, 'ok', lambda: True)
    monkeypatch.setattr(turtle_controller.time, 'monotonic', lambda: now[0])

    def spin_once(fake_node, timeout_sec):
        if fake_node.current_pose is None:
            fake_node.current_pose = Pose(x=0.1, y=0.1, theta=-math.pi)
            return

        command = fake_node.publisher.messages[-1]
        pose = fake_node.current_pose
        pose.theta = turtle_controller._normalize_angle(
            pose.theta + command.angular.z * timeout_sec)
        pose.x += command.linear.x * math.cos(pose.theta) * timeout_sec
        pose.y += command.linear.x * math.sin(pose.theta) * timeout_sec
        now[0] += timeout_sec

    monkeypatch.setattr(turtle_controller.rclpy, 'spin_once', spin_once)

    result = turtle_controller.TurtleControllerNode.move_turtle(
        node, 'turtle1', 11.0, 11.0)

    assert result is True, (now[0], node.current_pose.x, node.current_pose.y)
    assert now[0] <= turtle_controller.MOVEMENT_TIMEOUT


def test_move_turtle_returns_false_after_movement_deadline(monkeypatch):
    node = FakeController()
    now = [0.0]
    monkeypatch.setattr(turtle_controller.rclpy, 'ok', lambda: True)
    monkeypatch.setattr(turtle_controller.time, 'monotonic', lambda: now[0])

    def spin_once(fake_node, timeout_sec):
        if fake_node.current_pose is None:
            fake_node.current_pose = Pose(x=0.0, y=0.0, theta=0.0)
        else:
            now[0] += timeout_sec

    monkeypatch.setattr(turtle_controller.rclpy, 'spin_once', spin_once)

    result = turtle_controller.TurtleControllerNode.move_turtle(
        node, 'turtle1', 15.0, 0.0)

    assert result is False
    assert len(node.publisher.messages) > 1
    assert node.publisher.messages[-1].linear.x == 0.0
    assert node.publisher.messages[-1].angular.z == 0.0
    assert node.destroyed_subscription
    assert node.destroyed_publisher
