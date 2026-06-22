
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