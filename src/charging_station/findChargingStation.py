#!/usr/bin/env python


# Robo-Patrol: Find the charging station

import rospy
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
import roslib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, PoseWithCovarianceStamped, Point, Quaternion, Twist
from kobuki_msgs.msg import AutoDockingAction, AutoDockingGoal
import time
import batteryStatus


class FindChargingStation():

    nearChargingStationX = 0.0
    nearChargingStationY = 0.0    
    moveBase = False
    charging = False


    def __init__(self):
        rospy.init_node('findChargingStation')

	rospy.on_shutdown(self.shutdown)
	
	# tell the action client that we want to spin a thread by default
	moveBase = actionlib.SimpleActionClient("moveBase", MoveBaseAction)
	rospy.loginfo("wait for the action server to come up")
	# allow up to 30 seconds for the action server to come up
	moveBase.wait_for_server(rospy.Duration(30.0))


    # x and y coordinates for pose (position and orientation of the robot) should be approximately 1 metre from charging station
    def setCoordinatesNearChargingStation(x,y):
	self.nearChargingStationX = x
        self.nearChargingStationY = y


    def backUpFromChargingStation(self):
	# if you set a goal while it's docked it tends to run into the docking station while turning. Tell it to back up a little before
	if (charging):
	    rospy.loginfo("Docked to the charging station. Back up before next goal.")
	    cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
	    move_cmd = Twist()
	    # move forward [m/s]
	    move_cmd.linear.x = -0.1
	    # do not turn !! [radians/s]
	    move_cmd.angular.z = 0

	    rate = rospy.Rate(10)    # [Hz, (1/s)]
	    count = 0
	    backUpDuration = 20.0    # back up for 2 seconds
	    while (not rospy.is_shutdown() and count < backUpDuration):
	        cmd_vel.publish(move_cmd)
		count = count + 1
		rate.sleep()

	    # stop the TurtleBot
	    cmd_vel.publish(Twist())
	    return True


    def areWeCharging(self):
	return charging


    def doWeNeedPower(self):
	if (charging and (lowBaseBattery or lowNetbookBattery)):
	    rospy.loginfo("Charging... I'm fine :)")
	    time.sleep(30)
	    return False
	
	if (not charging and (lowBaseBattery or lowNetbookBattery)):
	    rospy.loginfo("Running low on petrol. Need to find a pumping station...")
	    dockWithChargingStation()
	    return True

	return False


    def dockWithChargingStation(self):
	# before we can run the auto-docking procedure we need to be close to the docking station
	if (not __goCloseToChargingStation()):
	    return False

	return __runAutoDocking()


    def __runAutoDocking(self):
	client = actionlib.SimpleActionClient('dock_drive_action', AutoDockingAction)
	waitForServer = 5.0
	rospy.loginfo("Waiting for auto docking")
	while not (client.wait_for_server(rospy.Duration(waitForServer))):
	    if rospy.is_shutdown():
		return
	    rospy.loginfo("Auto docking server is not connected. Still waiting...")

	rospy.loginfo("Auto docking server found")
	goal = AutoDockingGoal()

	waitForAutoDockResult = 180
	rospy.loginfo("Auto docking goal is set. Waiting for response...")
	client.send_goal(goal)

	if client.wait_for_result(rospy.Duration(waitForAutoDockResult)):
	    rospy.loginfo("Connected to the charging station")
	    charging = True
            # The callback which detects the docking status can take up to 3 seconds to update
	    # We are presuming it failed, even when the dock was successful. Therefore hardcoding this value after success.
	    return True
	else:
	    rospy.loginfo("Auto docking failed")
	    return False


    def __goCloseToChargingStation(self):
	rospy.loginfo("Let's go near the charging station")

	goal = MoveBaseGoal()
	goal.target_pose.header.frame_id = 'map'
	goal.target_pose.header.stamp = rospy.Time.now()

	# set a pose near the charging station
        # POSE = position + orientation <==> Point + Quaternion
	goal.target_pose.pose = Pose(Point(float(nearChargingStationX), float(nearChargingStationY), float(0)), Quaternion(float(0), float(0), float(0.5), float(-1.0)))

	# move it!
	moveBase.send_goal(goal)

	# allow TurtleBot up to 60 seconds to get close to the charging station
	success = moveBase.wait_for_result(rospy.Duration(60.0))

	if not success:
	    moveBase.cancel_goal()
	    rospy.loginfo("The base failed to reach the desired pose near the charging station")
	    return False
	else:
	    state = moveBase.get_state()
    	    if state == GoalStatus.SUCCEEDED:
	        rospy.loginfo("Hooray, reached the desired pose near the charging station")
	        return True
	    else:
                return False


    def shutdown(self):
        rospy.loginfo("Stop turtlebot")
	self.cmd_vel.publish(Twist())
        rospy.sleep(1)
