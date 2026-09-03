#include "rclcpp/rclcpp.hpp"
#include <chrono>
#include <functional>
#include "my_robot_interfaces/srv/set_led.hpp"

class BatteryNode : public rclcpp::Node
{
public:
    BatteryNode() : Node("battery"), elapsed_seconds_(0)
    {
        client_ = this->create_client<my_robot_interfaces::srv::SetLed>("set_led_panel_state");
        timer_ = this->create_wall_timer(
            std::chrono::seconds(1),
            std::bind(&BatteryNode::battery_callback, this));
    }

private:
    void battery_callback()
    {
        elapsed_seconds_++;

        if (elapsed_seconds_ == 4) {
            RCLCPP_INFO(this->get_logger(), "Battery is empty");
            callSetLedService(2, true);  // Turn on LED 2(zero based index)
        } else if (elapsed_seconds_ == 10) {
            RCLCPP_INFO(this->get_logger(), "Battery is charged");
            callSetLedService(2, false);  // Turn off LED 2(zero based index)
            elapsed_seconds_ = 0;
        }
    }
    void callSetLedService(int led_number, bool state)
    {
        auto request = std::make_shared<my_robot_interfaces::srv::SetLed::Request>();
        request->led_number = led_number;
        request->state = state;

        while (!client_->wait_for_service(std::chrono::seconds(1))) {
            if (!rclcpp::ok()) {
                RCLCPP_ERROR(this->get_logger(), "Interrupted while waiting for the service. Exiting.");
                return;
            }
            RCLCPP_INFO(this->get_logger(), "Service not available, waiting again...");
        }

        auto future = client_->async_send_request(request);
        try {
            auto response = future.get();
            if (response->success) {
                RCLCPP_INFO(this->get_logger(), "Successfully set LED %d to %s", led_number, state ? "ON" : "OFF");
            } else {
                RCLCPP_WARN(this->get_logger(), "Failed to set LED %d to %s", led_number, state ? "ON" : "OFF");
            }
        } catch (const std::exception & e) {
            RCLCPP_ERROR(this->get_logger(), "Service call failed: %s", e.what());
        }
    }

    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Client<my_robot_interfaces::srv::SetLed>::SharedPtr client_;
    int elapsed_seconds_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<BatteryNode>(); 
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

