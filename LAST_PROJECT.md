# todo
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

# 남은 작업
## 컨트롤러
- [ ] alive 거북이 토픽을 구독해서 내부에 변수로 관리하고, 기존의 get close... 메서드를 해당 내부변수를 이용하도록 변경하는작업
- [ ] kill 요청 서비스 호출
# 생성기
- [ ] spawn 쪽 : kill 거북이 요청을 받을 경우, 해당 거북이 kill하는 서비스 호출하고, 자신 내부 변수 상태 최신화.

# 통합
= [ ] 통합테스트
- [ ] 거북이 위치 이동 적절성 평가, 경우에 따라 기존 코드 원복.
- [ ]


#  easy run
ros2 launch my_robot_bringup turtle_track.launch.xml

# 참고

```sh
ros2 pkg create turtlesim_catch_them_all_py  --build-type ament_python --dependencies rclpy

ros2 pkg create turtlesim_catch_them_all_cpp --build-type ament_cmake --dependencies rclcpp

colcon build --packages-select turtlesim_catch_them_all_py turtlesim_catch_them_all_cpp

colcon build --packages-select my_robot_interfaces

colcon build --packages-select turtlesim_catch_them_all_py --symlink-install

colcon build --packages-select turtlesim_catch_them_all_cpp

colcon build --packages-select my_robot_bringup

setb
ros2 run turtlesim_catch_them_all_py turtle_controller

setb
ros2 run turtlesim_catch_them_all_cpp turtle_spawner

setb
ros2 run turtlesim turtlesim_node

```