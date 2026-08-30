#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"
using namespace std::placeholders;

class AddTwoIntsServerNode : public rclcpp::Node 
{
public:
    AddTwoIntsServerNode() : Node("add_two_ints_server") 
    {
        server_ = this->create_service<example_interfaces::srv::AddTwoInts>(
            "add_two_ints", 
            std::bind(&AddTwoIntsServerNode::handle_add_two_ints, this, _1, _2));
        RCLCPP_INFO(this->get_logger(), "Add Two Ints Service is ready.");
    }

private:
    void handle_add_two_ints(
        const example_interfaces::srv::AddTwoInts::Request::SharedPtr req,
        example_interfaces::srv::AddTwoInts::Response::SharedPtr res)
    {
        res->sum = req->a + req->b;
        RCLCPP_INFO(this->get_logger(), "Incoming request: a=%ld, b=%ld, sum=%ld", req->a, req->b, res->sum);
    }

    rclcpp::Service<example_interfaces::srv::AddTwoInts>::SharedPtr server_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<AddTwoIntsServerNode>(); 
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

