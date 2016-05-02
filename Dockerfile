FROM robopatrol/robopatrol-base:latest

ENV robopatrol_ws=/catkin_ws

# Init workspace
RUN /bin/bash -c 'source /opt/ros/indigo/setup.bash && \
mkdir -p $robopatrol_ws/src && \
catkin_init_workspace $robopatrol_ws/src'

WORKDIR $robopatrol_ws
COPY . $robopatrol_ws/src/robopatrol

# Build
RUN /bin/bash -c 'source /opt/ros/indigo/setup.bash && catkin_make'

# Start Simulation
CMD /bin/bash -c 'source $robopatrol_ws/devel/setup.bash && roslaunch robopatrol simulation.launch gui:=false'
