#include "rclcpp/rclcpp.hpp"

class TurtleSpawner  : public rclcpp::Node 
{
public:
    TurtleSpawner () : Node("turtle_spawner") 
    {
        RCLCPP_INFO(this->get_logger(), "%s begin", this->get_name());

        // 5초마다 turtle을 1개씩 생성한다. 이때 create_wall_timer를 사용할것.
        // Call the /spawn service to create a new turtle (choose random coordinates between 0.0 and 11.0 for both x and y)
        // 거북이 생성시 이름은 5글자의 영어 소문자로 랜덤하게 적용할것.
        // spawn servce의 양식은 아래 참고. turtlesim의 spawn 서비스를 호출하여 작업할것.
//         turtlesim/Spawn Service
// File: turtlesim/Spawn.srv
// Raw Message Definition
// float32 x
// float32 y
// float32 theta
// string name # Optional.  A unique name will be created and returned if this is empty
// ---
// string name
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

