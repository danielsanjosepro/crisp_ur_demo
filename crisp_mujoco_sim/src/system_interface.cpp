#include "crisp_mujoco_sim/system_interface.h"

#include <rclcpp/logging.hpp>
#include <rclcpp/clock.hpp>
#include <pluginlib/class_list_macros.hpp>

#include <string>
#include <thread>
#include <vector>
#include <memory>

#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"

namespace crisp_mujoco_sim
{

using CallbackReturn = rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

CallbackReturn Simulator::on_init(const hardware_interface::HardwareComponentInterfaceParams & params)
{
  RCLCPP_INFO(rclcpp::get_logger("Simulator"), "Initializing MuJoCo simulator...");

  // Call parent initialization
  if (hardware_interface::SystemInterface::on_init(params) != CallbackReturn::SUCCESS)
  {
    RCLCPP_ERROR(rclcpp::get_logger("Simulator"), "Base SystemInterface::on_init() failed");
    return CallbackReturn::ERROR;
  }

  // Access the parsed hardware info via the base class accessor
  const auto & info = get_hardware_info();

  if (info.joints.empty())
  {
    RCLCPP_ERROR(rclcpp::get_logger("Simulator"), "No joints found in hardware info.");
    return CallbackReturn::ERROR;
  }

  // Retrieve model parameter
  auto it = info.hardware_parameters.find("mujoco_model");
  if (it != info.hardware_parameters.end())
  {
    m_mujoco_model = it->second;
  }
  else
  {
    RCLCPP_WARN(rclcpp::get_logger("Simulator"),
                "Parameter 'mujoco_model' not provided; using default model path.");
    m_mujoco_model = "default_model.xml";
  }

  // Allocate joint state & command buffers
  const size_t n_joints = info.joints.size();
  m_positions.assign(n_joints, 0.0);
  m_velocities.assign(n_joints, 0.0);
  m_efforts.assign(n_joints, 0.0);
  m_effort_commands.assign(n_joints, 0.0);

  // Initialize ROS clock
  clock = std::make_shared<rclcpp::Clock>(RCL_ROS_TIME);

  // Launch the MuJoCo simulation thread
  m_simulation = std::thread(MuJoCoSimulator::simulate, m_mujoco_model);
  m_simulation.detach();

  RCLCPP_INFO(rclcpp::get_logger("Simulator"),
              "MuJoCo simulator initialized with model: %s (%zu joints)",
              m_mujoco_model.c_str(), n_joints);

  return CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface> Simulator::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;
  const auto & info = get_hardware_info();

  for (size_t i = 0; i < info.joints.size(); ++i)
  {
    state_interfaces.emplace_back(
      info.joints[i].name, hardware_interface::HW_IF_POSITION, &m_positions[i]);
    state_interfaces.emplace_back(
      info.joints[i].name, hardware_interface::HW_IF_VELOCITY, &m_velocities[i]);
    state_interfaces.emplace_back(
      info.joints[i].name, hardware_interface::HW_IF_EFFORT, &m_efforts[i]);
  }
  return state_interfaces;
}

std::vector<hardware_interface::CommandInterface> Simulator::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;
  const auto & info = get_hardware_info();

  for (size_t i = 0; i < info.joints.size(); ++i)
  {
    command_interfaces.emplace_back(
      info.joints[i].name, hardware_interface::HW_IF_EFFORT, &m_effort_commands[i]);
  }
  return command_interfaces;
}

Simulator::return_type Simulator::prepare_command_mode_switch(
  [[maybe_unused]] const std::vector<std::string> & start_interfaces,
  [[maybe_unused]] const std::vector<std::string> & stop_interfaces)
{
  return return_type::OK;
}

Simulator::return_type Simulator::read(
  [[maybe_unused]] const rclcpp::Time & time,
  [[maybe_unused]] const rclcpp::Duration & period)
{
  MuJoCoSimulator::getInstance().read(m_positions, m_velocities, m_efforts);
  return return_type::OK;
}

Simulator::return_type Simulator::write(
  [[maybe_unused]] const rclcpp::Time & time,
  [[maybe_unused]] const rclcpp::Duration & period)
{
  MuJoCoSimulator::getInstance().write(m_effort_commands);
  return return_type::OK;
}

}  // namespace crisp_mujoco_sim

PLUGINLIB_EXPORT_CLASS(crisp_mujoco_sim::Simulator, hardware_interface::SystemInterface)
