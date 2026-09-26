#include "my_robot_interfaces/srv/catch_turtle.hpp"
#include "my_robot_interfaces/msg/turtle_array.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp/executors/multi_threaded_executor.hpp"
#include "turtlesim/srv/kill.hpp"
#include "turtlesim/srv/spawn.hpp"

#include <algorithm>
#include <chrono>
#include <exception>
#include <functional>
#include <future>
#include <mutex>
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
        kill_client_callback_group_ =
            this->create_callback_group(rclcpp::CallbackGroupType::Reentrant);
        kill_client_ = this->create_client<turtlesim::srv::Kill>(
            "/kill",
            rclcpp::ServicesQoS(),
            kill_client_callback_group_);
        alive_turtles_publisher_ =
            this->create_publisher<my_robot_interfaces::msg::TurtleArray>("/alive_turtles", 10);
        catch_turtle_service_ = this->create_service<my_robot_interfaces::srv::CatchTurtle>(
            "catch_turtle",
            std::bind(
                &TurtleSpawner::handle_catch_turtle,
                this,
                std::placeholders::_1,
                std::placeholders::_2));
        timer_ = this->create_wall_timer(
            std::chrono::seconds(5),
            std::bind(&TurtleSpawner::spawn_turtle, this));
        alive_turtles_timer_ = this->create_wall_timer(
            std::chrono::milliseconds(500),
            std::bind(&TurtleSpawner::publish_alive_turtles, this));
    }

private:
    using Spawn = turtlesim::srv::Spawn;
    using Kill = turtlesim::srv::Kill;
    using CatchTurtle = my_robot_interfaces::srv::CatchTurtle;

    static constexpr unsigned int kMaxRetries = 3;

    rclcpp::Client<Spawn>::SharedPtr spawn_client_;
    rclcpp::Client<Kill>::SharedPtr kill_client_;
    rclcpp::CallbackGroup::SharedPtr kill_client_callback_group_;
    rclcpp::Publisher<my_robot_interfaces::msg::TurtleArray>::SharedPtr alive_turtles_publisher_;
    rclcpp::Service<CatchTurtle>::SharedPtr catch_turtle_service_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::TimerBase::SharedPtr alive_turtles_timer_;
    std::mt19937 random_engine_;
    std::uniform_real_distribution<float> coordinate_distribution_{0.0f, 11.0f};
    std::uniform_real_distribution<float> theta_distribution_{0.0f, 6.28318530718f};
    std::uniform_int_distribution<int> letter_distribution_{'a', 'z'};
    std::unordered_set<std::string> used_names_;
    std::unordered_set<std::string> pending_catch_names_;
    std::vector<my_robot_interfaces::msg::Turtle> alive_turtles_;
    std::mutex state_mutex_;
    bool spawn_pending_{false};

    void handle_catch_turtle(
        const std::shared_ptr<CatchTurtle::Request> request,
        std::shared_ptr<CatchTurtle::Response> response)
    {
        response->result = false;

        if (!request || request->name.empty()) {
            RCLCPP_WARN(this->get_logger(), "Cannot catch a turtle with an empty name.");
            return;
        }

        bool turtle_removed = false;
        {
            std::lock_guard<std::mutex> lock(state_mutex_);
            const auto turtle_it = std::find_if(
                alive_turtles_.begin(),
                alive_turtles_.end(),
                [&request](const auto & turtle) { return turtle.name == request->name; });
            if (turtle_it == alive_turtles_.end()) {
                RCLCPP_WARN(
                    this->get_logger(),
                    "Cannot catch unknown turtle '%s'.",
                    request->name.c_str());
                return;
            }

            if (!pending_catch_names_.insert(request->name).second) {
                RCLCPP_WARN(
                    this->get_logger(),
                    "Catch request for turtle '%s' is already in progress.",
                    request->name.c_str());
                return;
            }
        }

        const auto clear_pending = [this, name = request->name]() {
            std::lock_guard<std::mutex> lock(state_mutex_);
            pending_catch_names_.erase(name);
        };

        try {
            if (!kill_client_->wait_for_service(std::chrono::milliseconds(0))) {
                RCLCPP_WARN(this->get_logger(), "/kill service is not available.");
                clear_pending();
                return;
            }

            auto kill_request = std::make_shared<Kill::Request>();
            kill_request->name = request->name;
            auto future = kill_client_->async_send_request(kill_request);
            if (future.wait_for(std::chrono::seconds(2)) != std::future_status::ready) {
                RCLCPP_ERROR(
                    this->get_logger(),
                    "Timed out while killing turtle '%s'.",
                    request->name.c_str());
                clear_pending();
                return;
            }

            if (!future.get()) {
                RCLCPP_ERROR(
                    this->get_logger(),
                    "The /kill service returned an empty response for turtle '%s'.",
                    request->name.c_str());
                clear_pending();
                return;
            }

            {
                std::lock_guard<std::mutex> lock(state_mutex_);
                const auto turtle_it = std::find_if(
                    alive_turtles_.begin(),
                    alive_turtles_.end(),
                    [&request](const auto & turtle) { return turtle.name == request->name; });
                if (turtle_it == alive_turtles_.end()) {
                    RCLCPP_ERROR(
                        this->get_logger(),
                        "Turtle '%s' disappeared before the catch completed.",
                        request->name.c_str());
                } else {
                    alive_turtles_.erase(turtle_it);
                    turtle_removed = true;
                }
            }
            if (!turtle_removed) {
                clear_pending();
                return;
            }
            publish_alive_turtles();
            response->result = true;
            RCLCPP_INFO(this->get_logger(), "Caught turtle '%s'.", request->name.c_str());
        } catch (const std::exception & exception) {
            RCLCPP_ERROR(
                this->get_logger(),
                "Failed to catch turtle '%s': %s",
                request->name.c_str(),
                exception.what());
        }

        clear_pending();
    }

    void spawn_turtle()
    {
        {
            std::lock_guard<std::mutex> lock(state_mutex_);
            if (spawn_pending_) {
                RCLCPP_WARN(
                    this->get_logger(),
                    "Previous spawn request is still pending; skipping this tick.");
                return;
            }

            if (!spawn_client_->service_is_ready()) {
                RCLCPP_WARN(this->get_logger(), "/spawn service is not available; skipping this tick.");
                return;
            }

            spawn_pending_ = true;
        }

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
            {
                std::lock_guard<std::mutex> lock(state_mutex_);
                alive_turtles_.push_back(std::move(turtle));
                spawn_pending_ = false;
            }
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

        {
            std::lock_guard<std::mutex> lock(state_mutex_);
            spawn_pending_ = false;
        }
        RCLCPP_ERROR(
            this->get_logger(),
            "Spawn failed after %u retries: %s",
            kMaxRetries,
            reason.c_str());
    }

    void publish_alive_turtles()
    {
        my_robot_interfaces::msg::TurtleArray message;
        {
            std::lock_guard<std::mutex> lock(state_mutex_);
            message.list = alive_turtles_;
        }
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

            std::lock_guard<std::mutex> lock(state_mutex_);
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
    rclcpp::executors::MultiThreadedExecutor executor(rclcpp::ExecutorOptions(), 2);
    executor.add_node(node);
    executor.spin();
    rclcpp::shutdown();
    return 0;
}
