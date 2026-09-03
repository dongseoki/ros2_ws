#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/msg/string.hpp"

class LedPanelNode : public rclcpp::Node 
{
public:
    LedPanelNode() : Node("led_panel") 
    {
        publisher_ = this->create_publisher<example_interfaces::msg::String>("led_panel", 10); 
        timer_ = this->create_wall_timer(
            std::chrono::seconds(1),
            std::bind(&LedPanelNode::publish_led_status, this));                                     
        RCLCPP_INFO(this->get_logger(), "LED Panel node has been started and is publishing LED status.");
    }

private:
    void publish_led_status()
    {
        auto message = example_interfaces::msg::String();
        message.data = "LED Panel is operational.";
        publisher_->publish(message);
        RCLCPP_INFO(this->get_logger(), "Published LED status: '%s'", message.data.c_str());
    }

    rclcpp::Publisher<example_interfaces::msg::String>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<LedPanelNode>(); 
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

