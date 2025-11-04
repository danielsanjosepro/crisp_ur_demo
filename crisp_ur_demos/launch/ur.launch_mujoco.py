import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchContext, LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
    Shutdown,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def robot_description_dependent_nodes_spawner(
    context: LaunchContext,
    ur_type,
    robot_ip,
    use_fake_hardware,
    start_robot_state_publisher,
    use_rviz,
):
    ur_type_str = context.perform_substitution(ur_type)
    robot_ip_str = context.perform_substitution(robot_ip)
    use_fake_hardware_str = context.perform_substitution(use_fake_hardware)

    crisp_pkg = get_package_share_directory("crisp_ur_demos")
    ur_xacro = os.path.join(crisp_pkg, "config", "ur.urdf.xacro")
    robot_description = xacro.process_file(
        ur_xacro,
        mappings={
            "name": "ur",
            "robot_ip": robot_ip_str,
            "use_mock_hardware": use_fake_hardware_str,
            "ur_type": ur_type_str,
        },
    ).toprettyxml(indent="  ")

    controllers_yaml = os.path.join(crisp_pkg, "config", "ur_controllers.yaml")
    rviz_file = os.path.join(crisp_pkg, "config", "view_robot.rviz")

    return [
        Node(
            package="joint_state_publisher",
            executable="joint_state_publisher",
            name="joint_state_publisher",
            parameters=[{"rate": 1000}],
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description}],
            condition=IfCondition(start_robot_state_publisher),
        ),
        Node(
            package="controller_manager",
            executable="ros2_control_node",
            parameters=[controllers_yaml, {"robot_description": robot_description}],
            output={"stdout": "screen", "stderr": "screen"},
            on_exit=Shutdown(),
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["joint_state_broadcaster"],
            output="screen",
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["scaled_joint_trajectory_controller"],
            output="screen",
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["cartesian_impedance_controller", "--inactive"],
            output="screen",
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["joint_impedance_controller", "--inactive"],
            output="screen",
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["gravity_compensation", "--inactive"],
            output="screen",
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["pose_broadcaster"],
            output="screen",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["--display-config", rviz_file],
            condition=IfCondition(use_rviz),
        ),
    ]


def generate_launch_description():
    ur_type_parameter_name = "ur_type"
    robot_ip_parameter_name = "robot_ip"
    use_fake_hardware_parameter_name = "use_fake_hardware"
    use_rviz_parameter_name = "use_rviz"
    start_robot_state_publisher_name = "start_robot_state_publisher"

    ur_type = LaunchConfiguration(ur_type_parameter_name)
    robot_ip = LaunchConfiguration(robot_ip_parameter_name)
    use_fake_hardware = LaunchConfiguration(use_fake_hardware_parameter_name)
    use_rviz = LaunchConfiguration(use_rviz_parameter_name)
    start_robot_state_publisher = LaunchConfiguration(start_robot_state_publisher_name)

    robot_description_dependent_nodes_spawner_opaque_function = OpaqueFunction(
        function=robot_description_dependent_nodes_spawner,
        args=[
            ur_type,
            robot_ip,
            use_fake_hardware,
            start_robot_state_publisher,
            use_rviz,
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                ur_type_parameter_name,
                default_value="ur10e",
                description="UR type (mujoco only supported for ur10e in this package)",
            ),
            DeclareLaunchArgument(
                robot_ip_parameter_name,
                default_value="192.168.56.101",
                description="IP address of the URSim/robot / real robot",
            ),
            DeclareLaunchArgument(
                use_fake_hardware_parameter_name,
                default_value="false",
                description="Use fake hardware / simulator",
            ),
            DeclareLaunchArgument(
                use_rviz_parameter_name,
                default_value="false",
                description="Visualize the robot in Rviz",
            ),
            DeclareLaunchArgument(
                start_robot_state_publisher_name,
                default_value="true",
                description="Start robot_state_publisher node",
            ),
            robot_description_dependent_nodes_spawner_opaque_function,
        ]
    )
