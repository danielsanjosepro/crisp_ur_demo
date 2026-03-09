> [!WARN]
> Consider using https://github.com/danielsanjosepro/pixi_ur_ros2.git instead as it simplifies a lot the installation pipeline.

> [!NOTE]
> ```bash
> git clone https://github.com/danielsanjosepro/crisp_ur_demo.git
> cd crisp_ur_demo
> docker compose build
> docker compose up launch_ur
> ```

# crisp_ur_demo

Demo on how to use Universal Robots (UR) with CRISP Controllers using Docker containers.

This repository provides a Docker-based setup to test [CRISP controllers](https://github.com/utiasDSL/crisp_controllers) with Universal Robots using the [UR ROS2 Driver](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver) with effort interface support.

## Overview

This demo is based on the structure of [crisp_controllers_demos](https://github.com/utiasDSL/crisp_controllers_demos) but adapted specifically for Universal Robots. It uses a fork of the UR ROS2 driver ([urfeex/Universal_Robots_ROS2_Driver](https://github.com/urfeex/Universal_Robots_ROS2_Driver/tree/effort_interface)) that implements the effort interface required for CRISP controllers.

## Features

- Docker container setup for easy deployment
- Support for all UR robot types (UR3, UR3e, UR5, UR5e, UR10, UR10e, UR16e, UR20, UR30)
- Integration with CRISP controllers (Cartesian and Joint impedance control)
- Real hardware and fake hardware modes
- Multiple middleware options (FastDDS, CycloneDDS, Zenoh)

## Prerequisites

- Docker and Docker Compose installed
- X11 server for GUI applications (RViz)
- (For real hardware) Network connection to UR robot

## Quick Start

1. Clone this repository:
```bash
git clone https://github.com/danielsanjosepro/crisp_ur_demo.git
cd crisp_ur_demo
```

2. Validate your setup (optional but recommended):
```bash
./scripts/validate_setup.sh
```

3. Copy and configure the environment file:
```bash
cp .env.example .env
# Edit .env to set your robot IP and type
```

4. Build the Docker container:
```bash
docker compose build
```

5. Run the demo:
```bash
# For fake hardware (simulation)
docker compose run --rm launch_ur

# For real hardware, first set the environment variables in .env:
# UR_FAKE_HARDWARE=false
# ROBOT_IP=<your_robot_ip>
# UR_TYPE=<your_robot_type>
docker compose run --rm launch_ur
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Robot configuration
UR_FAKE_HARDWARE=false        # Set to true for simulation
ROBOT_IP=192.168.56.101       # Your robot's IP address
UR_TYPE=ur5e                  # Robot type (ur3, ur3e, ur5, ur5e, ur10, ur10e, ur16e, ur20, ur30)

# Middleware configuration (optional)
# RMW=cyclone                 # Use CycloneDDS
# RMW=zenoh                   # Use Zenoh
# RMW=fastdds                 # Use FastDDS (default)

# Network configuration (optional)
# ROS_NETWORK_INTERFACE=eth0  # Network interface for ROS 2
```

### Available Controllers

The demo includes the following CRISP controllers:

- `cartesian_impedance_controller` - Cartesian space impedance control
- `joint_impedance_controller` - Joint space impedance control
- `gravity_compensation` - Gravity compensation controller
- `pose_broadcaster` - Publishes end-effector pose
- `twist_broadcaster` - Publishes end-effector twist

And standard UR controllers:
- `scaled_joint_trajectory_controller` - Trajectory controller with speed scaling
- `joint_trajectory_controller` - Standard trajectory controller
- `forward_effort_controller` - Direct effort control

## Project Structure

```
crisp_ur_demo/
├── docker/
│   └── Dockerfile.ur           # Docker build file for UR setup
├── docker-compose.yaml         # Docker compose configuration
├── scripts/
│   ├── setup_middleware.sh     # Middleware configuration script
│   ├── set_cyclone_config.sh   # CycloneDDS setup
│   ├── set_zenoh_config.sh     # Zenoh setup
│   └── validate_setup.sh       # Setup validation script
├── config/
│   └── cyclonedds.xml          # CycloneDDS configuration
├── crisp_ur_demos/             # ROS 2 package
│   ├── launch/
│   │   └── ur.launch.py        # Main launch file
│   ├── config/
│   │   └── ur_controllers.yaml # Controller configurations
│   ├── package.xml             # ROS 2 package manifest
│   └── setup.py                # Python package setup
├── .env.example                # Example environment configuration
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Usage

### Interactive Shell

To get an interactive shell inside the container:

```bash
docker compose run --rm devcontainer
```

### Starting Controllers

Once the robot is running, you can switch between controllers using ros2 control:

```bash
# List available controllers
ros2 control list_controllers

# Load and start cartesian impedance controller
ros2 control set_controller_state cartesian_impedance_controller start

# Switch to joint impedance controller
ros2 control switch_controllers --deactivate cartesian_impedance_controller --activate joint_impedance_controller
```

## Troubleshooting

### Docker Build Issues

If the build fails, try:
```bash
docker compose build --no-cache
```

### Connection Issues with Real Robot

1. Ensure the robot is powered on and connected to the network
2. Verify you can ping the robot: `ping <robot_ip>`
3. Check that the robot is in remote control mode
4. Ensure the External Control URCap is installed on the robot

### RViz Not Displaying

Ensure X11 forwarding is enabled:
```bash
xhost +local:docker
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the Apache-2.0 License.

## References

- [CRISP Controllers](https://github.com/utiasDSL/crisp_controllers)
- [CRISP Controllers Demos](https://github.com/utiasDSL/crisp_controllers_demos)
- [UR ROS2 Driver with Effort Interface](https://github.com/urfeex/Universal_Robots_ROS2_Driver/tree/effort_interface)
- [Universal Robots ROS2 Driver](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver)
