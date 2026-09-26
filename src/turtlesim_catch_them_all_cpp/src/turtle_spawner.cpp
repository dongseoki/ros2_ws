#include "rclcpp/rclcpp.hpp"

class TurtleSpawner  : public rclcpp::Node 
{
public:
    TurtleSpawner () : Node("turtle_spawner") 
    {
        RCLCPP_INFO(this->get_logger(), "%s begin", this->get_name());
    }

private:
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TurtleSpawner >(); 
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

