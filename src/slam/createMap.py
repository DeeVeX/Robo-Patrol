#!/usr/bin/env python

import subprocess
import time
import time
import rospy


class CreateMap():

    def __init__(self):
	self.saveMap()

    """
    @param : String bagfile (path + filename)
    simulates a patrol by playing back (= publishing messages) a rosbag file
    make sure you set the ROS parameter use_sim_time to TRUE before calling 'rosbag play'
    An instance of slam_mapping (package gmapping) must be active
    Normally, this is done when launching mapping.launch, but if you want to do it manually:
    rosrun gmapping slam_mapping
    """
    def playBackRecording(self,bagfile):
	if not bagfile == "":
	    self.__setROSparams()
            time.sleep(1)
	    subprocess.call("rosbag play --clock " + bagfile, shell=True)


    def __setROSparams(self):
	subprocess.call("rosparam set use_sim_time true", shell=True)


    """
    An instance of slam_mapping (package gmapping) must be active before calling saveMap
    map_server service generates two files:
    - an image (THE MAP)
    - map.yaml (map meta data)
    """
    def saveMap(self):
	subprocess.call("rosrun map_server map_saver", shell=True)
	

if __name__ == "__main__":
    CreateMap()
