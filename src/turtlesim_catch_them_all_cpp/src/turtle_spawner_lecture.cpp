#include "rclcpp/rclcpp.hpp"
#include "turtlesim/srv/spawn.hpp"

#include <chrono>
#include <cmath>
#include <functional>
#include <memory>
#include <random>
#include <string>

class TurtleSpawnerLecture : public rclcpp::Node
{
public:
    TurtleSpawnerLecture()
    : Node("turtle_spawner"),
      random_engine_(std::random_device{}()),
      coordinate_distribution_(0.0, 11.0),
      theta_distribution_(0.0, 2.0 * std::acos(-1.0))
    {
        spawn_client_ = this->create_client<turtlesim::srv::Spawn>("/spawn");
        spawn_turtle_timer_ = this->create_wall_timer(
            std::chrono::seconds(2),
            std::bind(&TurtleSpawnerLecture::spawn_new_turtle, this));
    }

private:
    using Spawn = turtlesim::srv::Spawn;

    rclcpp::Client<Spawn>::SharedPtr spawn_client_;
    rclcpp::TimerBase::SharedPtr spawn_turtle_timer_;
    std::mt19937 random_engine_;
    std::uniform_real_distribution<double> coordinate_distribution_;
    std::uniform_real_distribution<double> theta_distribution_;
    const std::string turtle_name_prefix_{"turtle"};
    unsigned int turtle_counter_{0};

    void spawn_new_turtle()
    {
        ++turtle_counter_;
        const std::string name = turtle_name_prefix_ + std::to_string(turtle_counter_);
        const double x = coordinate_distribution_(random_engine_);
        const double y = coordinate_distribution_(random_engine_);
        const double theta = theta_distribution_(random_engine_);
        call_spawn_service(name, x, y, theta);
    }

    void call_spawn_service(const std::string & name, double x, double y, double theta)
    {
        while (!spawn_client_->wait_for_service(std::chrono::seconds(1))) {
            RCLCPP_WARN(this->get_logger(), "waiting for spawn service...");
        }

        auto request = std::make_shared<Spawn::Request>();
        request->x = static_cast<float>(x);
        request->y = static_cast<float>(y);
        request->theta = static_cast<float>(theta);
        request->name = name;

        spawn_client_->async_send_request(
            request,
            [this](rclcpp::Client<Spawn>::SharedFuture future) {
                callback_call_spawn_service(future);
            });
    }

    void callback_call_spawn_service(rclcpp::Client<Spawn>::SharedFuture future)
    {
        try {
            const auto response = future.get();
            if (response && !response->name.empty()) {
                RCLCPP_INFO(
                    this->get_logger(),
                    "New alive turtle: %s",
                    response->name.c_str());
            }
        } catch (const std::exception & exception) {
            RCLCPP_ERROR(
                this->get_logger(),
                "Spawn request failed: %s",
                exception.what());
        }
    }
};

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<TurtleSpawnerLecture>());
    rclcpp::shutdown();
    return 0;
}
