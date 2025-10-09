# Copyright (c) 2024
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, Shutdown
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Declare arguments
    ur_type_arg = DeclareLaunchArgument(
        "ur_type",
        default_value="ur5e",
        description="Type/series of used UR robot.",
        choices=["ur3", "ur3e", "ur5", "ur5e", "ur10", "ur10e", "ur16e", "ur20", "ur30"],
    )
    
    robot_ip_arg = DeclareLaunchArgument(
        "robot_ip",
        default_value="192.168.56.101",
        description="IP address by which the robot can be reached.",
    )
    
    use_fake_hardware_arg = DeclareLaunchArgument(
        "use_fake_hardware",
        default_value="false",
        description="Start robot with fake hardware mirroring command to its states.",
    )
    
    use_rviz_arg = DeclareLaunchArgument(
        "use_rviz",
        default_value="false",
        description="Start RViz for visualization.",
    )

    # Initialize Arguments
    ur_type = LaunchConfiguration("ur_type")
    robot_ip = LaunchConfiguration("robot_ip")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")
    use_rviz = LaunchConfiguration("use_rviz")

    # Get the ur_robot_driver package share directory
    ur_robot_driver_path = FindPackageShare("ur_robot_driver")
    
    # Controllers configuration file
    controllers_file = PathJoinSubstitution(
        [
            FindPackageShare("crisp_ur_demos"),
            "config",
            "ur_controllers.yaml",
        ]
    )

    # Include UR control launch file
    ur_control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [ur_robot_driver_path, "launch", "ur_control.launch.py"]
            )
        ),
        launch_arguments={
            "ur_type": ur_type,
            "robot_ip": robot_ip,
            "use_mock_hardware": use_fake_hardware,
            "controllers_file": controllers_file,
            "launch_rviz": use_rviz,
            "initial_joint_controller": "scaled_joint_trajectory_controller",
        }.items(),
    )

    return LaunchDescription(
        [
            ur_type_arg,
            robot_ip_arg,
            use_fake_hardware_arg,
            use_rviz_arg,
            ur_control,
        ]
    )
