#!/usr/bin/env python

import subprocess
import time, datetime
import psutil, getpass, sys
import rospy


"""
optional, when running this script from a terminal:
pass 'recording duration' (int) as first parameter
The unit is seconds. ex.: python recordMap.py 30
"""

class RecordMap(object):
    # static class variables
    username = ""
    recordingDuration = 15  # [s]


    def __init__(self):
	duration = self.recordingDuration
	try:
	    self.username = getpass.getuser()
            if len(sys.argv) > 1:
		duration = int(sys.argv[1])
	except Exception as error:
	    print "Can't get username.", repr(error)
	    sys.exit(2)

        bagfile = self.startRecording(duration)
	time.sleep(1)

	print "finished recording to", bagfile


    def getRecordingDuration(self):
	return self.recordingDuration


    def setRecordingDuration(self,duration):
	self.recordingDuration = duration

    """
    @param : int duration [seconds]
    Returns the name of the bag file
    A bag file (see rosbag documentation) is a container of recorded messages
    """
    def startRecording(self,duration):
	timestamp = time.time()
	now = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d_%H-%M-%S")

	bagfilePath = "/home/" + self.username + "/catkin_ws/src/robopatrol/"
        bagfile = bagfilePath + "robopatrol_" + now + ".bag"

	print "Starting the recording process..."
	subprocess.call("rosbag record --duration=" + str(duration) + " -O " + bagfile + " scan tf", shell=True)

	return bagfile


    # not being used, just for debugging
    def __killParentAndChildrenProcesses(self,ppid):
	parent = psutil.Process(ppid)

	for child in parent.children(recursive=True):
	    child.kill()
	parent.kill()


    # not being used, just for debugging
    def __killProcess(self,proc):
	try:
	    count = 0
            while proc.is_alive() and count < 10:
	        proc.terminate()
	   	count = count + 1
		time.sleep(1)

	    if proc.is_alive():
                raise Excetption("cannot terminate the process " + proc.name)
	    else:
		return 0
        except:
	    print("cannot terminate the process " + proc.name)
            return -1
	

if __name__ == "__main__":
    RecordMap()
