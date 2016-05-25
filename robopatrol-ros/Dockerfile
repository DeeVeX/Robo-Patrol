FROM ros:indigo-ros-base

RUN apt-get update -y \
&& apt-get install -y \
ros-indigo-turtlebot \
ros-indigo-turtlebot-apps \
ros-indigo-turtlebot-interactions \
ros-indigo-zeroconf-avahi \
ros-indigo-rosbridge-suite \
ros-indigo-turtlebot-simulator \
ros-indigo-kobuki-ftdi \
ros-indigo-rocon-remocon \
ros-indigo-rocon-qt-library \
ros-indigo-ar-track-alvar-msgs \
build-essential python-twisted \
python-pip \
&& rm -rf /var/lib/apt/lists/*

