#include "rclcpp/rclcpp.hpp"
#include "my_robot_interfaces/msg/hardware_status.hpp"

class HardwareStatusPublisherNode : public rclcpp::Node
{
public:
    HardwareStatusPublisherNode() : Node("hardware_status_publisher")
    {
        publisher_ = this->create_publisher<my_robot_interfaces::msg::HardwareStatus>("hardware_status", 10);
        timer_ = this->create_wall_timer(
            std::chrono::seconds(1),
            std::bind(&HardwareStatusPublisherNode::publish_hardware_status, this));
        RCLCPP_INFO(this->get_logger(), "Hardware Status Publisher node has been started and is publishing hardware status.");
    }

private:
    void publish_hardware_status()
    {
        auto msg = my_robot_interfaces::msg::HardwareStatus();
        // Populate the message with hardware status information
        msg.temperature = 42.0; // Example temperature value
        msg.are_motors_ready = true; // Example motor readiness status
        msg.debug_message = "All systems operational"; // Example debug message
        publisher_->publish(msg);
    }

    rclcpp::Publisher<my_robot_interfaces::msg::HardwareStatus>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<HardwareStatusPublisherNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

