#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"

using namespace std::chrono_literals;

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<rclcpp::Node>("add_two_ints_client");

    auto client = node->create_client<example_interfaces::srv::AddTwoInts>("add_two_ints");
    while (!client->wait_for_service(1s)) {
        if (!rclcpp::ok()) {
            RCLCPP_ERROR(node->get_logger(), "Interrupted while waiting for the service. Exiting.");
            return 0;
        }
        RCLCPP_INFO(node->get_logger(), "Service not available, waiting again...");
    }

    auto request = std::make_shared<example_interfaces::srv::AddTwoInts::Request>();
    request->a = 10;
    request->b = 20;

    auto future = client->async_send_request(request);
    rclcpp::spin_until_future_complete(node, future);

    auto response = future.get();

    RCLCPP_INFO(node->get_logger(), "Result: %ld", response->sum);

    rclcpp::shutdown();
    return 0;
}

