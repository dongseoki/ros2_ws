cmake_minimum_required(VERSION 3.8)
project(turtlesim_catch_them_all_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(turtlesim REQUIRED)
find_package(my_robot_interfaces REQUIRED)

add_executable(turtle_spawner src/turtle_spawner.cpp)
ament_target_dependencies(turtle_spawner rclcpp turtlesim my_robot_interfaces)

add_executable(turtle_controller_lecture src/turtle_controller_lecture.cpp)
ament_target_dependencies(turtle_controller_lecture rclcpp geometry_msgs turtlesim)

add_executable(turtle_spawner_lecture src/turtle_spawner_lecture.cpp)
ament_target_dependencies(turtle_spawner_lecture rclcpp turtlesim)

install(TARGETS
  turtle_spawner
  turtle_controller_lecture
  turtle_spawner_lecture
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
