ARG ROS_DISTRO=rolling
ARG CRISP_CONTROLLERS_VERSION=1.1.0

FROM osrf/ros:${ROS_DISTRO}-desktop AS base

ENV ROS_DISTRO=${ROS_DISTRO}

# Create a non-root user
ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-c"]

# Delete existing user if it exists
RUN if getent passwd ${USER_UID}; then \
    userdel -r $(getent passwd ${USER_UID} | cut -d: -f1); \
    fi

# Delete existing group if it exists
RUN if getent group ${USER_GID}; then \
    groupdel $(getent group ${USER_GID} | cut -d: -f1); \
    fi

RUN groupadd --gid $USER_GID $USERNAME \
  && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
  && mkdir /home/$USERNAME/.config && chown $USER_UID:$USER_GID /home/$USERNAME/.config

# Set up sudo
RUN apt-get update \
  && apt-get install -y sudo \
  && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME\
  && chmod 0440 /etc/sudoers.d/$USERNAME \
  && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    vim \
    build-essential \
    cmake \
    wget \
    git \
    unzip \
    pip \
    python3-venv \
    python3-flake8 \
    python3-rosdep \
    python3-setuptools \
    python3-vcstool \
    python3-colcon-common-extensions \
    cmake \
    libpoco-dev \
    libeigen3-dev \
    ros-$ROS_DISTRO-ros2-control \
    ros-$ROS_DISTRO-ros2-controllers \
    ros-$ROS_DISTRO-rmw-cyclonedds-cpp \
    ros-$ROS_DISTRO-rmw-zenoh-cpp \
    dpkg

# Symlink python3 to python
RUN ln -s /usr/bin/python3 /usr/bin/python

USER $USERNAME

RUN mkdir -p /home/ros/ros2_ws

WORKDIR /home/ros/ros2_ws

FROM base AS ur

# === UR ROS2 with effort interface ===
# Clone the UR driver with effort interface support
RUN git clone --branch effort_interface https://github.com/urfeex/Universal_Robots_ROS2_Driver.git src/Universal_Robots_ROS2_Driver \
    && source /opt/ros/${ROS_DISTRO}/setup.bash \
    && sudo apt-get update \
    && cd src/Universal_Robots_ROS2_Driver \
    && vcs import .. < Universal_Robots_ROS2_Driver.${ROS_DISTRO}.repos --recursive --skip-existing || true \
    && cd /home/ros/ros2_ws \
    && rosdep update \
    && rosdep install --from-paths src --ignore-src --rosdistro $ROS_DISTRO -y \
    && colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release \
    && find src/Universal_Robots_ROS2_Driver -mindepth 1 -maxdepth 1 -type d -exec touch {}/COLCON_IGNORE \;

FROM ur AS ur-overlay

ARG CRISP_CONTROLLERS_VERSION=1.1.0

COPY . src/crisp_ur_demo

RUN git clone --branch $ROS_DISTRO --depth 1 https://github.com/utiasDSL/crisp_controllers.git src/crisp_controllers

RUN source /opt/ros/$ROS_DISTRO/setup.bash \
    && source /home/ros/ros2_ws/install/setup.bash \
    && sudo apt update \
    && rosdep update \
    && rosdep install -q --from-paths src --ignore-src -y \
    && colcon build --symlink-install \
        --cmake-args -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON --packages-select crisp_controllers crisp_ur_demos
