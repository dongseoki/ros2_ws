#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/msg/string.hpp"
#include <string>

using namespace std::chrono_literals;

class RobotNewsStationNode : public rclcpp::Node
{
public:
    RobotNewsStationNode    () : Node("robot_news_station")
    {
        this->declare_parameter<std::string>("robot_name", "R2D2");
        robot_name_ =  this->get_parameter("robot_name").as_string();
        publisher_ = this->create_publisher<example_interfaces::msg::String>("robot_news", 10);
        timer_ = this->create_wall_timer(
            0.5s,
            std::bind(&RobotNewsStationNode::publish_news, this));                                     
        RCLCPP_INFO(this->get_logger(), "Robot News Station node has been started and is publishing news.");
    }

private:
    void publish_news()
    {
        auto message = example_interfaces::msg::String();
        message.data = "Breaking news from the Robot News Station!" + robot_name_;
        publisher_->publish(message);
        RCLCPP_INFO(this->get_logger(), "Published news: '%s'", message.data.c_str());
    }
    rclcpp::Publisher<example_interfaces::msg::String>::SharedPtr publisher_;
    std::string robot_name_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<RobotNewsStationNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

