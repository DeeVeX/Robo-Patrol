FROM ros:indigo-ros-base

RUN sudo apt-get update -y

# Turtlebot packages
RUN sudo apt-get install -y \
ros-indigo-turtlebot \
ros-indigo-turtlebot-apps \
ros-indigo-turtlebot-interactions \
ros-indigo-zeroconf-avahi \
ros-indigo-rosbridge-suite \
ros-indigo-turtlebot-simulator \
ros-indigo-kobuki-ftdi \
ros-indigo-rocon-remocon \
ros-indigo-rocon-qt-library \
ros-indigo-ar-track-alvar-msgs

# Packages for catkin build and rosbridge
RUN sudo apt-get install -y build-essential python-twisted

# Make image smaller
RUN sudo rm -rf /var/lib/apt/lists/*

