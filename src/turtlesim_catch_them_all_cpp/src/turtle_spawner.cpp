#include "my_robot_interfaces/msg/turtle_array.hpp"
#include "rclcpp/rclcpp.hpp"
#include "turtlesim/srv/spawn.hpp"

#include <chrono>
#include <exception>
#include <functional>
#include <random>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

class TurtleSpawner : public rclcpp::Node
{
public:
    TurtleSpawner() : Node("turtle_spawner"), random_engine_(std::random_device{}())
    {
        RCLCPP_INFO(this->get_logger(), "%s begin", this->get_name());

        spawn_client_ = this->create_client<turtlesim::srv::Spawn>("/spawn");
        alive_turtles_publisher_ =
            this->create_publisher<my_robot_interfaces::msg::TurtleArray>("/alive_turtles", 10);
        timer_ = this->create_wall_timer(
            std::chrono::seconds(5),
            std::bind(&TurtleSpawner::spawn_turtle, this));
        alive_turtles_timer_ = this->create_wall_timer(
            std::chrono::milliseconds(500),
            std::bind(&TurtleSpawner::publish_alive_turtles, this));
    }

private:
    using Spawn = turtlesim::srv::Spawn;

    static constexpr unsigned int kMaxRetries = 3;

    rclcpp::Client<Spawn>::SharedPtr spawn_client_;
    rclcpp::Publisher<my_robot_interfaces::msg::TurtleArray>::SharedPtr alive_turtles_publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::TimerBase::SharedPtr alive_turtles_timer_;
    std::mt19937 random_engine_;
    std::uniform_real_distribution<float> coordinate_distribution_{0.0f, 11.0f};
    std::uniform_real_distribution<float> theta_distribution_{0.0f, 6.28318530718f};
    std::uniform_int_distribution<int> letter_distribution_{'a', 'z'};
    std::unordered_set<std::string> used_names_;
    std::vector<my_robot_interfaces::msg::Turtle> alive_turtles_;
    bool spawn_pending_{false};

    void spawn_turtle()
    {
        if (spawn_pending_) {
            RCLCPP_WARN(this->get_logger(), "Previous spawn request is still pending; skipping this tick.");
            return;
        }

        if (!spawn_client_->service_is_ready()) {
            RCLCPP_WARN(this->get_logger(), "/spawn service is not available; skipping this tick.");
            return;
        }

        spawn_pending_ = true;
        send_spawn_request(0);
    }

    void send_spawn_request(unsigned int retry_count)
    {
        auto request = std::make_shared<Spawn::Request>();
        request->x = coordinate_distribution_(random_engine_);
        request->y = coordinate_distribution_(random_engine_);
        request->theta = theta_distribution_(random_engine_);
        request->name = generate_name();

        RCLCPP_INFO(
            this->get_logger(),
            "Requesting turtle '%s' at x=%.2f, y=%.2f, theta=%.2f",
            request->name.c_str(),
            request->x,
            request->y,
            request->theta);

        const float x_pos = request->x;
        const float y_pos = request->y;
        spawn_client_->async_send_request(
            request,
            [this, retry_count, x_pos, y_pos](rclcpp::Client<Spawn>::SharedFuture future) {
                handle_spawn_response(future, retry_count, x_pos, y_pos);
            });
    }

    void handle_spawn_response(
        rclcpp::Client<Spawn>::SharedFuture future,
        unsigned int retry_count,
        float x_pos,
        float y_pos)
    {
        try {
            const auto response = future.get();
            if (!response || response->name.empty()) {
                handle_spawn_failure("service returned an empty turtle name", retry_count);
                return;
            }

            my_robot_interfaces::msg::Turtle turtle;
            turtle.name = response->name;
            turtle.x_pos = x_pos;
            turtle.y_pos = y_pos;
            alive_turtles_.push_back(std::move(turtle));

            spawn_pending_ = false;
            RCLCPP_INFO(this->get_logger(), "Spawned turtle '%s'.", response->name.c_str());
        } catch (const std::exception & exception) {
            handle_spawn_failure(exception.what(), retry_count);
        }
    }

    void handle_spawn_failure(const std::string & reason, unsigned int retry_count)
    {
        if (retry_count < kMaxRetries) {
            RCLCPP_WARN(
                this->get_logger(),
                "Spawn failed (%s); retrying immediately (%u/%u).",
                reason.c_str(),
                retry_count + 1,
                kMaxRetries);
            send_spawn_request(retry_count + 1);
            return;
        }

        spawn_pending_ = false;
        RCLCPP_ERROR(
            this->get_logger(),
            "Spawn failed after %u retries: %s",
            kMaxRetries,
            reason.c_str());
    }

    void publish_alive_turtles()
    {
        my_robot_interfaces::msg::TurtleArray message;
        message.list = alive_turtles_;
        alive_turtles_publisher_->publish(message);
    }

    std::string generate_name()
    {
        while (true) {
            std::string name;
            name.reserve(5);
            while (name.size() < 5) {
                name.push_back(static_cast<char>(letter_distribution_(random_engine_)));
            }

            if (used_names_.insert(name).second) {
                return name;
            }
        }
    }
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TurtleSpawner>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
