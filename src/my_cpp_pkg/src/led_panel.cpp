#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/msg/string.hpp"
#include "my_robot_interfaces/msg/led_panel_state.hpp"

class LedPanelNode : public rclcpp::Node 
{
public:
    LedPanelNode() : Node("led_panel"), current_led_states{}
    {
        publisher_ = this->create_publisher<my_robot_interfaces::msg::LedPanelState>("led_panel_state", 10); 
        // TODO implement interface my_robot_interfaces::srv::SetLed.
        service_ = this->create_service<my_robot_interfaces::srv::SetLed>(
            "set_led_panel_state",
            std::bind(&LedPanelNode::set_led_panel_state, this, std::placeholders::_1, std::placeholders::_2)
        );
        timer_ = this->create_wall_timer(
            std::chrono::seconds(1),
            std::bind(&LedPanelNode::publish_led_status, this));                                     
        RCLCPP_INFO(this->get_logger(), "LED Panel node has been started and is publishing LED status.");
    }

private:
    void publish_led_status()
    {

        publisher_->publish(current_led_states);
        RCLCPP_INFO(
            this->get_logger(),
            "Published LED status: [%d, %d, %d]",
            current_led_states.led_states[0],
            current_led_states.led_states[1],
            current_led_states.led_states[2]
        );
    }
    void set_led_panel_state(
        const std::shared_ptr<my_robot_interfaces::srv::SetLed::Request> request,
        std::shared_ptr<my_robot_interfaces::srv::SetLed::Response> response)
    {
        // current_led_states.led_states[request.led_number] = request ->state
        // current_led_states.led_states = request->led_states;
        response->success = true;
        RCLCPP_INFO(
            this->get_logger(),
            "Received request to set LED status to: [%d, %d, %d]",
            current_led_states.led_states[0],
            current_led_states.led_states[1],
            current_led_states.led_states[2]
        );
    }

    rclcpp::Publisher<my_robot_interfaces::msg::LedPanelState>::SharedPtr publisher_;
    rclcpp::Service<my_robot_interfaces::srv::SetLed>::SharedPtr service_;
    rclcpp::TimerBase::SharedPtr timer_;
    my_robot_interfaces::msg::LedPanelState current_led_states;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<LedPanelNode>(); 
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

