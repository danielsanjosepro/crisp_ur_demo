# Copyright (c) 2024
#
# Licensed under the Apache License, Version 2.0 (the "License").
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import UnlessCondition


def generate_launch_description():
    # ----------------------------
    # Declare launch arguments
    # ----------------------------
    ur_type_arg = DeclareLaunchArgument(
        "ur_type",
        default_value="ur10e",
        description="Type/series of used UR robot.",
        choices=[
            "ur3",
            "ur3e",
            "ur5",
            "ur5e",
            "ur10",
            "ur10e",
            "ur16e",
            "ur20",
            "ur30",
        ],
    )

    robot_ip_arg = DeclareLaunchArgument(
        "robot_ip",
        default_value="192.168.56.101",
        description="IP address of the URSim/robot.",
    )

    use_fake_hardware_arg = DeclareLaunchArgument(
        "use_fake_hardware",
        default_value="false",
        description="Use fake hardware (URSim).",
    )

    use_rviz_arg = DeclareLaunchArgument(
        "use_rviz",
        default_value="false",
        description="Launch RViz for visualization.",
    )

    # ----------------------------
    # Initialize LaunchConfigurations
    # ----------------------------
    ur_type = LaunchConfiguration("ur_type")
    robot_ip = LaunchConfiguration("robot_ip")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")
    use_rviz = LaunchConfiguration("use_rviz")

    # ----------------------------
    # Include UR control launch
    # ----------------------------
    ur_robot_driver_path = FindPackageShare("ur_robot_driver")

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
            "launch_rviz": use_rviz,
            "controllers_file": PathJoinSubstitution(
                [FindPackageShare("crisp_ur_demos"), "config", "ur_controllers.yaml"]
            ),
            "initial_joint_controller": "scaled_joint_trajectory_controller",
        }.items(),
    )

    # ----------------------------
    # Base controllers required for URSim
    # ----------------------------
    # joint_state_broadcaster = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["joint_state_broadcaster"],
    #     output="screen",
    # )

    # tcp_pose_broadcaster = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["tcp_pose_broadcaster"],
    #     output="screen",
    # )

    # ----------------------------
    # Custom controllers
    # ----------------------------
    cartesian_impedance_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["cartesian_impedance_controller", "--inactive"],
        output="screen",
    )

    joint_impedance_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_impedance_controller", "--inactive"],
        output="screen",
    )

    gravity_compensation = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gravity_compensation", "--inactive"],
        output="screen",
    )

    pose_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["pose_broadcaster"],
        output="screen",
    )

    Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_admittance_controller", "--inactive"],
        output="screen",
    ),

    # ----------------------------
    # URSim connection nodes
    # ----------------------------
    # urscript_interface = Node(
    #     package="ur_robot_driver",
    #     executable="urscript_interface",
    #     parameters=[{"robot_ip": robot_ip}],
    #     output="screen",
    #     condition=UnlessCondition(use_fake_hardware),
    # )

    # robot_state_helper_node = Node(
    #     package="ur_robot_driver",
    #     executable="robot_state_helper",
    #     name="ur_robot_state_helper",
    #     output="screen",
    #     parameters=[{"robot_ip": robot_ip}],
    # )

    # trajectory_until_node = Node(
    #     package="ur_robot_driver",
    #     executable="trajectory_until_node",
    #     name="trajectory_until_node",
    #     output="screen",
    # )

    # ----------------------------
    # LaunchDescription
    # ----------------------------
    # Only include the UR driver launch. Do not spawn controllers already managed by ur_control.launch.py.
    return LaunchDescription(
        [
            ur_type_arg,
            robot_ip_arg,
            use_fake_hardware_arg,
            use_rviz_arg,
            ur_control,
            # Uncomment the following lines ONLY if these controllers are NOT managed by ur_control.launch.py
            cartesian_impedance_controller,
            joint_impedance_controller,
            gravity_compensation,
            pose_broadcaster,
        ]
    )
