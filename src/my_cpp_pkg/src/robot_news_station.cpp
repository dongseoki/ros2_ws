#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/msg/string.hpp"

using namespace std::chrono_literals;

class RobotNewsStationNode : public rclcpp::Node // MODIFY NAME
{
public:
    RobotNewsStationNode    () : Node("robot_news_station"), robot_name_("R2D2") // MODIFY NAME
    {
        publisher_ = this->create_publisher<example_interfaces::msg::String>("robot_news", 10); // TOPIC NAME
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
    auto node = std::make_shared<RobotNewsStationNode>(); // MODIFY NAME
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

