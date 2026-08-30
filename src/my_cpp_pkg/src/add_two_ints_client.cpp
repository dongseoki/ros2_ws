#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"

using namespace std::placeholders;

class AddTwoIntsClientNode : public rclcpp::Node 
{
public:
    AddTwoIntsClientNode() : Node("add_two_ints_client") 
    {
        client_ = this->create_client<example_interfaces::srv::AddTwoInts>("add_two_ints");
    }
    void callAddTwoInts(int a, int b) 
    {
        while (!client_->wait_for_service(std::chrono::seconds(1))) {
            if (!rclcpp::ok()) {
                RCLCPP_ERROR(this->get_logger(), "Interrupted while waiting for the service. Exiting.");
                return;
            }
            RCLCPP_INFO(this->get_logger(), "Service not available, waiting again...");
        }

        auto request = std::make_shared<example_interfaces::srv::AddTwoInts::Request>();
        request->a = a;
        request->b = b;

        auto future = client_->async_send_request(request, std::bind(&AddTwoIntsClientNode::callbackCallAddTwoInts, this, std::placeholders::_1));
    }

private:
    void callbackCallAddTwoInts(rclcpp::Client<example_interfaces::srv::AddTwoInts>::SharedFuture future) 
    {
        auto response = future.get();
        RCLCPP_INFO(this->get_logger(), "Result: %ld", response->sum);
    }
    rclcpp::Client<example_interfaces::srv::AddTwoInts>::SharedPtr client_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<AddTwoIntsClientNode>(); 
    node->callAddTwoInts(3, 5); // Example call with a=3 and b=5
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

