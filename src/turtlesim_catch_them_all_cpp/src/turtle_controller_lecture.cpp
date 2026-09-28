#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "turtlesim/msg/pose.hpp"

#include <chrono>
#include <cmath>
#include <functional>
#include <memory>

class TurtleControllerLecture : public rclcpp::Node
{
public:
    TurtleControllerLecture() : Node("turtle_controller")
    {
        cmd_vel_publisher_ =
            this->create_publisher<geometry_msgs::msg::Twist>("/turtle1/cmd_vel", 10);
        pose_subscriber_ = this->create_subscription<turtlesim::msg::Pose>(
            "/turtle1/pose",
            10,
            std::bind(&TurtleControllerLecture::callback_pose, this, std::placeholders::_1));
        control_loop_timer_ = this->create_wall_timer(
            std::chrono::milliseconds(10),
            std::bind(&TurtleControllerLecture::control_loop, this));
    }

private:
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_publisher_;
    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr pose_subscriber_;
    rclcpp::TimerBase::SharedPtr control_loop_timer_;
    turtlesim::msg::Pose pose_;
    bool has_pose_{false};
    const double target_x_{2.0};
    const double target_y_{8.0};

    void callback_pose(const turtlesim::msg::Pose::SharedPtr pose)
    {
        pose_ = *pose;
        has_pose_ = true;
    }

    void control_loop()
    {
        if (!has_pose_) {
            return;
        }

        const double dist_x = target_x_ - pose_.x;
        const double dist_y = target_y_ - pose_.y;
        const double distance = std::sqrt(dist_x * dist_x + dist_y * dist_y);
        geometry_msgs::msg::Twist cmd;

        if (distance > 0.5) {
            cmd.linear.x = 2.0 * distance;

            const double goal_theta = std::atan2(dist_y, dist_x);
            double diff = goal_theta - pose_.theta;
            const double pi = std::acos(-1.0);
            if (diff > pi) {
                diff -= 2.0 * pi;
            } else if (diff < -pi) {
                diff += 2.0 * pi;
            }
            cmd.angular.z = 6.0 * diff;
        } else {
            cmd.linear.x = 0.0;
            cmd.angular.z = 0.0;
        }

        cmd_vel_publisher_->publish(cmd);
    }
};

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<TurtleControllerLecture>());
    rclcpp::shutdown();
    return 0;
}
