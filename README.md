
```sh
  1  /opt/ros/jazzy/setup.bash
    2  source /opt/ros/jazzy/setup.bash
    3  ros2
    4  arch
    5  pwd
    6  ls
    7  vi ~/.bashrc
    8  cd ros2_ws/src/
    9  ls
   10  ros2 pkg create my_py_pkg --build-type ament_python --dependencies rclpy
   11  clear
   12  history
   13  ls
   14  code .
   15  cd ..
   16  colcon build
   17  colcon build --packages-select my_pk_pkg
```

* do not colcon build inside src folder
```

  47  cd ros2_ws/src/
   48  ros2 pkg create my_cpp_pkg --build-type ament_cmake --dependencies rclcpp

cd ros2_ws/src/
10  ros2 pkg create my_py_pkg --build-type ament_python --dependencies rclpy
   51  colcon build
   52  colcon build --packages-select my_cpp_pkg
```

# write a python node
* exeutable name
* node name
* file name -> my_first_node
```sh
source ~/.bashrc
ros2 run my_py_pkg py_node

```

# python node with OOP
* colcon build --packages-select my_py_pkg
* source install/setup.bash
* ros2 run my_py_pkg py_node

# cpp node
* colcon build --packages-select my_cpp_pkg
* source install/setup.bash
* ros2 run my_cpp_pkg cpp_node

# python publisher
```sh
colcon build --packages-select my_py_pkg --symlink-install
ros2 run my_py_pkg robot_news_station
ros2 topic echo /robot_news
```

# python subscriber
```sh
colcon build --packages-select my_py_pkg --symlink-install
ros2 run my_py_pkg smartphone
```
* ros2 interface show example_interfaces/msg/String

# cpp publisher
```sh
colcon build --packages-select my_cpp_pkg
source install/setup.bash
ros2 run my_cpp_pag robot_news_station
ros2 node list
ros2 node info /robot_news_station
ros2 topic echo /robot_news
```

# cpp subscriber
```sh
ros2 node list
ros2 node info /smartphone_node
ros2 run my_cpp_pkg robot_news_station
ros2 run my_cpp_pkg smartphone
```

# section5, activity02
```sh
ros2 interface show example_interfaces/msg/Int64
colcon build --packages-select my_py_pkg --symlink-install
ros2 run my_py_pkg number_publisher
ros2 topic echo /number
```

# section5, activity02 finish
```sh
colcon build --packages-select my_py_pkg --symlink-install
source install/setup.bash
ros2 run my_py_pkg number_publisher
```

In another terminal, source the workspace and run the counter:

```sh
source install/setup.bash
ros2 run my_py_pkg number_counter
```

In a third terminal, source the workspace and observe the accumulated values:

```sh
source install/setup.bash
ros2 topic echo /number_count
```

The publisher sends `2` every second, so `/number_count` should output `2`,
`4`, `6`, and so on. The counter log should also show the initial value `0`
and each updated accumulated value.

# section 06
## python server
```sh
s_ros
cd ros_ws
ros2 run my_py_pkg add_two_ints_server
ros2 interface show example_interfaces/srv/AddTwoInts
colcon build --packages-select my_py_pkg --symlink-install
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 3, b: 7}"
```
## python client no oop
```sh
ros2 run my_py_pkg add_two_ints_client_no_oop
```

## python client with oop
```
```
## cpp server
```sh
cd ~/ros2_ws
s_ros
colcon build --packages-select my_cpp_pkg
ros2 run my_cpp_pkg add_two_ints_server

cd ~/ros2_ws
s_ros
ros2 run my_py_pkg add_two_ints_client_no_oop


```

## cpp client
```sh
cd ~/ros2_ws
s_ros
ros2 run my_cpp_pkg add_two_ints_client_no_oop

```

# inspect service
```sh
370  ros2 service list
  371  ros2 service -h
  372  ros2 service info /add_two_ints
  373  ros2 service type /add_two_ints
  374  ros2 interface show example_interfaces/srv/AddTwoInts
  375  rqt

  ros2 run my_py_pkg add_two_ints_server --ros-args -r /add_two_ints:=/my_service

```

# activity06
```sh
colcon build --packages-select my_py_pkg --symlink-install
ros2 run my_py_pkg number_publisher
ros2 run my_py_pkg number_counter
ros2 topic echo /number_count
ros2 service call /reset_counter example_interfaces/srv/SetBool "{data: true}"
ros2 service call /reset_counter example_interfaces/srv/SetBool "{data: false}"
```
# section07 custom interfaces
```sh
colcon build --packages-select my_robot_interfaces 
source ~/.bashrc
ros2 interface list | grep my_robot
ros2 interface show my_robot_interfaces/msg/HardwareStatus
```

## custom interface with python
```sh
colcon build --packages-select my_py_pkg --symlink-install
ros2 run my_py_pkg hardware_status_publisher

source ~/.bashrc
ros2 topic echo /hardware_status

```

## custom interface with cpp
```sh
# before this must check .vscode/c_cpp_properties.json
colcon build --packages-select my_cpp_pkg
ros2 run my_cpp_pkg hardware_status_publisher

source ~/.bashrc
ros2 topic echo /hardware_status

```
## custom srv
```sh
colcon build --packages-select my_robot_interfaces

source ~/.bashrc
ds@ds-vm:~/ros2_ws$ ros2 interface show my_robot_interfaces/srv/ComputeRectangleArea
float64 length
float64 width
---
float64 area
```

## activity07
```sh
colcon build --packages-select my_robot_interfaces
ros2 topic echo /led_panel_state

ros2 interface show my_robot_interfaces/msg/LedPanelState

colcon build --packages-select my_cpp_pkg
ros2 run my_cpp_pkg led_panel

ros2 topic echo /led_panel_state

ros2 run my_cpp_pkg battery

```