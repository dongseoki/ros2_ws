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
from types import SimpleNamespace

from turtlesim.msg import Pose

from turtlesim_catch_them_all_py import turtle_controller


class FakePublisher:
    """Collect messages published by a controller call."""

    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append(message)


class FakeFuture:
    """Provide a controllable service response future."""

    def __init__(self, response=None, error=None, completed=True):
        self.response = response
        self.error = error
        self.completed = completed

    def done(self):
        """Return whether the fake request has completed."""
        return self.completed

    def result(self):
        """Return the response, or raise the configured service error."""
        if self.error is not None:
            raise self.error
        return self.response

    def exception(self):
        """Return the configured service error."""
        return self.error


class FakeCatchTurtleClient:
    """Capture catch requests and provide a configured service future."""

    def __init__(self, future, service_available=True):
        """Initialize the fake client with a result and availability state."""
        self.future = future
        self.service_available = service_available
        self.request = None

    def wait_for_service(self, timeout_sec):
        """Return service availability and remember the timeout."""
        self.timeout_sec = timeout_sec
        return self.service_available

    def call_async(self, request):
        """Capture the request and return its configured future."""
        self.request = request
        return self.future


class FakeLogger:
    """Collect controller log messages."""

    def __init__(self):
        """Initialize collections for each log level."""
        self.errors = []
        self.warnings = []
        self.infos = []

    def error(self, message):
        """Record an error message."""
        self.errors.append(message)

    def warning(self, message):
        """Record a warning message."""
        self.warnings.append(message)

    def info(self, message):
        """Record an info message."""
        self.infos.append(message)


class FakeController:
    """Provide fake node operations needed by controller tests."""

    def __init__(self):
        """Initialize fake state for movement and service tests."""
        self.current_pose = None
        self.alive_turtles = []
        self.publisher = FakePublisher()
        self.destroyed_publisher = False

    def pose_callback(self, message):
        """Store the latest pose message."""
        self.current_pose = message

    def create_publisher(self, *_args):
        """Return the fake velocity publisher."""
        return self.publisher

    def destroy_publisher(self, _publisher):
        """Record that the fake publisher was destroyed."""
        self.destroyed_publisher = True


def test_catch_turtle_sends_name_and_returns_success(monkeypatch):
    """Send the turtle name and return the successful service result."""
    node = FakeController()
    node.catch_turtle_client = FakeCatchTurtleClient(
        FakeFuture(response=SimpleNamespace(result=True)))
    node.get_logger = lambda: FakeLogger()
    monkeypatch.setattr(turtle_controller.rclpy, 'ok', lambda: True)

    result = turtle_controller.TurtleControllerNode.catch_turtle(
        node, 'turtle_a')

    assert result is True
    assert node.catch_turtle_client.request.name == 'turtle_a'
    assert node.catch_turtle_client.timeout_sec == (
        turtle_controller.CATCH_SERVICE_WAIT_TIMEOUT)


def test_catch_turtle_returns_false_when_service_unavailable():
    """Report a missing catch service without sending a request."""
    node = FakeController()
    node.catch_turtle_client = FakeCatchTurtleClient(
        FakeFuture(), service_available=False)
    node.logger = FakeLogger()
    node.get_logger = lambda: node.logger

    result = turtle_controller.TurtleControllerNode.catch_turtle(
        node, 'turtle_a')

    assert result is False
    assert node.catch_turtle_client.request is None
    assert node.logger.errors


def test_catch_turtle_returns_false_when_service_rejects_request(monkeypatch):
    """Return false and log a warning when the service rejects the catch."""
    node = FakeController()
    node.catch_turtle_client = FakeCatchTurtleClient(
        FakeFuture(response=SimpleNamespace(result=False)))
    node.logger = FakeLogger()
    node.get_logger = lambda: node.logger
    monkeypatch.setattr(turtle_controller.rclpy, 'ok', lambda: True)

    result = turtle_controller.TurtleControllerNode.catch_turtle(
        node, 'turtle_a')

    assert result is False
    assert node.logger.warnings


def test_catch_turtle_times_out_waiting_for_response(monkeypatch):
    """Return false and log an error when the response times out."""
    node = FakeController()
    node.catch_turtle_client = FakeCatchTurtleClient(
        FakeFuture(completed=False))
    node.logger = FakeLogger()
    node.get_logger = lambda: node.logger
    now = iter([0.0, turtle_controller.CATCH_RESPONSE_TIMEOUT])
    monkeypatch.setattr(turtle_controller.time, 'monotonic', lambda: next(now))
    monkeypatch.setattr(turtle_controller.rclpy, 'ok', lambda: True)

    result = turtle_controller.TurtleControllerNode.catch_turtle(
        node, 'turtle_a')

    assert result is False
    assert node.logger.errors


def test_catch_turtle_reports_service_exception(monkeypatch):
    """Return false and log an exception raised by the service."""
    node = FakeController()
    node.catch_turtle_client = FakeCatchTurtleClient(
        FakeFuture(error=RuntimeError('service failed')))
    node.logger = FakeLogger()
    node.get_logger = lambda: node.logger
    monkeypatch.setattr(turtle_controller.rclpy, 'ok', lambda: True)

    result = turtle_controller.TurtleControllerNode.catch_turtle(
        node, 'turtle_a')

    assert result is False
    assert 'service failed' in node.logger.errors[0]


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


def test_alive_turtles_callback_stores_published_list():
    node = FakeController()
    turtles = [SimpleNamespace(name='turtle_a', x_pos=1.0, y_pos=2.0)]

    turtle_controller.TurtleControllerNode.alive_turtles_callback(
        node, SimpleNamespace(list=turtles))

    assert node.alive_turtles is turtles


def test_get_close_turtle_returns_nearest_turtle():
    node = FakeController()
    node.current_pose = Pose(x=3.0, y=4.0, theta=0.0)
    node.alive_turtles = [
        SimpleNamespace(name='far', x_pos=10.0, y_pos=10.0),
        SimpleNamespace(name='nearest', x_pos=4.0, y_pos=4.0),
        SimpleNamespace(name='also_far', x_pos=0.0, y_pos=0.0),
    ]

    result = turtle_controller.TurtleControllerNode.get_close_turtle(node)

    assert result == ('nearest', 4.0, 4.0)


def test_get_close_turtle_returns_none_without_pose_or_turtles():
    node = FakeController()
    node.alive_turtles = [
        SimpleNamespace(name='turtle_a', x_pos=1.0, y_pos=2.0)]
    assert turtle_controller.TurtleControllerNode.get_close_turtle(node) is None

    node.current_pose = Pose(x=3.0, y=4.0, theta=0.0)
    node.alive_turtles = []
    assert turtle_controller.TurtleControllerNode.get_close_turtle(node) is None


def test_move_turtle_reaches_goal_and_stops(monkeypatch):
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
    assert node.destroyed_publisher
