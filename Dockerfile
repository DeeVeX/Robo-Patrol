FROM robopatrol/ros:latest

ENV robopatrol_ws=/catkin_ws

# Init workspace
RUN /bin/bash -c 'source /opt/ros/indigo/setup.bash && \
mkdir -p $robopatrol_ws/src && \
catkin_init_workspace $robopatrol_ws/src'

RUN /bin/bash -c 'git clone git://github.com/tu-darmstadt-ros-pkg/hector_models.git $robopatrol_ws/src/hector_models/ \
&& git clone git://github.com/robopeak/rplidar_ros.git $robopatrol_ws/src/rplidar_ros/'

RUN pip install "git+https://github.com/agronholm/apscheduler.git"

WORKDIR $robopatrol_ws
COPY . $robopatrol_ws/src/robopatrol

# Build
RUN pip install -r src/robopatrol/requirements.txt
RUN /bin/bash -c 'source /opt/ros/indigo/setup.bash && catkin_make'

# Start Simulation
CMD /bin/bash -c 'source $robopatrol_ws/devel/setup.bash && roslaunch robopatrol simulation.launch gui:=false'
