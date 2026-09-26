1. 컨트롤 노드 먼저 완성.
1-1 임의 좌표까지 움직이는 것 구현.
1-2 핵심 비즈니스 로직 구현 
WHILE(){
    // 가장 가까운 거북을 찾는다.
    // 이동한다.
    // 도착하면 해당 거북을 제거한다.
}
2. spawn 노드 완성.
3. 컨트롤에서 더미 씌운거를 spawn노드랑 통일.
4. 런치 파일 통합.


```sh
ros2 pkg create turtlesim_catch_them_all_py  --build-type ament_python --dependencies rclpy

ros2 pkg create turtlesim_catch_them_all_cpp --build-type ament_cmake --dependencies rclcpp

colcon build --packages-select turtlesim_catch_them_all_py turtlesim_catch_them_all_cpp

colcon build --packages-select turtlesim_catch_them_all_py --symlink-install

colcon build --packages-select turtlesim_catch_them_all_cpp

source install/setup.bash

setb
ros2 run turtlesim_catch_them_all_py turtle_controller

setb
ros2 run turtlesim_catch_them_all_cpp turtle_spawner

```