#!/usr/bin/env python

'''
Node: Autonomous driving
Author: R. Georgiou
Version: 1.0
Last modified: 29.04.2016


This implementation uses a SimpleActionClient to connect to an ActionServer.

*** IMPORT ***
AMCL is used for localization and therefore this node assumes, that we are using a map!
Can be an empty map aswell, though.

All relevant information regarding navigation can be found here:
http://wiki.ros.org/navigation

The move_base package provides an implementation of an action (see the actionlib package) that,
given a goal in the world, will attempt to reach it with a mobile base.
The move_base node links together a global and local planner to accomplish its global navigation task.
full description:  http://wiki.ros.org/move_base

tf is a package that lets the user keep track of multiple coordinate frames over time.
A robotic system typically has many coordinate frames, such as a world frame, base frame, 
laserscan frame etc.
With tf we can maintain the relationship between coordinate frames in a tree structure.
'''

import rospy
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import *
import move_base_msgs.msg
import nav_msgs.msg
import tf
import math


class AutonomousPatrol():

     # reference coordinate frame, used in the MoveBaseGoal message
     # base_footprint	attached to the mobile base	
    _coordinateFrame = 'base_footprint'
    # [m]
    _defaultDistance = 2


    def __init__(self):

	rospy.init_node('Autonomous_RoboPatrol', anonymous=False)

	# method stop is called in case of shutdown or failure
	rospy.on_shutdown(self.stop)

	# Constructs a SimpleActionClient and opens connections to an ActionServer.
	#The move_base package provides an implementation of an action.
	self.client = actionlib.SimpleActionClient('move_base', move_base_msgs.msg.MoveBaseAction)
	
	# Wait for the action server to report that it has come up and is ready to begin processing goals.
	# Blocks until the action server connects to this client.
	rospy.loginfo('Waiting for the action server to come up.')
	self.client.wait_for_server()
	rospy.loginfo('The action server is online.')
	
	# Listen to the transforms
        self.tfListener = tf.listener.TransformListener()

	'''
        I add the odomPose just in case we want to query the current position and orientation of the robot.

	The variable odomPose holds the current pose based on odometry, which is tied to /base_footprint.

	Odometry Raw Message Definition:
	This represents an ESTIMATE of a position and velocity in free space.  
	The pose in this message should be specified in the coordinate frame given by header.frame_id.
	The twist in this message should be specified in the coordinate frame given by the child_frame_id
		Header header
		string child_frame_id
		geometry_msgs/PoseWithCovariance pose
		geometry_msgs/TwistWithCovariance twist
	'''
	self.odomPose = nav_msgs.msg.Odometry()

        # get current pose from odometry and store it in global variable currentPose
        rospy.Subscriber('odom', nav_msgs.msg.Odometry, self._setCurrentOdomPoseCallback)

	self.pos, self.quat = self._getCurrentPosition()
	rospy.loginfo(self.pos)
	rospy.loginfo(self.quat)
	#self._publishInitialPose()


    def _setCurrentOdomPoseCallback(self, pose):
	self.odomPose = pose


    '''
    type: geometry_msgs/PoseWithCovariance Message
    	Pose pose
	float64 covariance
    '''
    def getCurrentOdomPose(self):
	return self.odomPose


    '''
    Cancels all goals prior to a given timestamp.
    This preempts all goals running on the action server for which the time stamp is earlier
    than the specified time stamp this message is serviced by the ActionServer.
    '''
    def stop(self):

 	self.client.cancel_goals_at_and_before_time(rospy.Time.now())
	rospy.loginfo('stopping')
	
	pub = rospy.Publisher('cmd_vel_mux/input/teleop', Twist, queue_size=10)

	twist = Twist()
	twist.linear.x = 0
	twist.linear.y = 0
	twist.linear.z = 0
	twist.angular.x = 0
	twist.angular.y = 0
	twist.angular.z = 0

	rospy.loginfo('Sending a series of twist commands to make sure the robot stops.')

	for i in range(0,5):
	    pub.publish(twist)

	rospy.loginfo('Robot has stopped.')


    '''
    Starts the autonomous patrol.
    '''
    def run(self):

        rospy.loginfo('Starting the initial mapping of the surrounding area...')

	# Do a complete rotation (2*PI) and let the robot discover its surroundings
	rad = 90 * math.pi / 180
	for i in range(0,3):
	    self._rotate(rad)

	rospy.loginfo('Mapping of the surrounding area is complete.')
	rospy.loginfo('Ready to run.')

	'''
	*************************************************************************************************

	This is the main loop.
	Now for the fun part, the actual exploration!

	*************************************************************************************************
	'''
	while not rospy.is_shutdown():

	    # create a goal	    
	    goal = move_base_msgs.msg.MoveBaseGoal()

	    # set coordinate frame
	    goal.target_pose.header.frame_id = self._coordinateFrame

            # set time stamp
	    goal.target_pose.header.stamp = rospy.Time.now()

	    # set the pose (position + orientation)
	    # position
	    goal.target_pose.pose.position.x = self._defaultDistance
	    goal.target_pose.pose.position.y = 0
	    goal.target_pose.pose.position.z = 0
	    # orientation
	    goal.target_pose.pose.orientation.x = 0
	    goal.target_pose.pose.orientation.y = 0
	    goal.target_pose.pose.orientation.z = 0
	    goal.target_pose.pose.orientation.w = 1

	    # send the navigation goal to the navigation stack
	    if not rospy.is_shutdown():
	        self.client.send_goal(goal)

	    success = self.client.wait_for_result(rospy.Duration(30))

	    if not success:
                self.client.cancel_goal()
                rospy.loginfo("The base failed to reach the goal.")
    	    else:
		state = self.client.get_state()
		if state == GoalStatus.SUCCEEDED:
		    rospy.loginfo("MoveBaseGoal reached, yay! Team RoboPatrol FTW !")


    def _rotate(self, rad):

	quaternionDifference = tf.transformations.quaternion_about_axis(rad, (0, 0, 1))
	position, quaternion = self._getCurrentPosition()

        transformedQuaternion = tf.transformations.quaternion_multiply(quaternion, quaternionDifference)
	rotatorGoal = move_base_msgs.msg.MoveBaseGoal()

 	rospy.loginfo(quaternion)
	rospy.loginfo(quaternionDifference)

	# set coordinate frame
	rotatorGoal.target_pose.header.frame_id = self._coordinateFrame

        # set time stamp
	rotatorGoal.target_pose.header.stamp = rospy.Time.now()

	# set the pose (position + orientation)
	# position (3d point)
	rotatorGoal.target_pose.pose.position.x = position[0]
	rotatorGoal.target_pose.pose.position.y = position[1]
	rotatorGoal.target_pose.pose.position.z = position[2]
	# orientation
	rotatorGoal.target_pose.pose.orientation.x = transformedQuaternion[0]
	rotatorGoal.target_pose.pose.orientation.y = transformedQuaternion[1]
	rotatorGoal.target_pose.pose.orientation.z = transformedQuaternion[2]
	rotatorGoal.target_pose.pose.orientation.w = transformedQuaternion[3]

	# send the rotator goal to the navigation stack
        self.client.send_goal(rotatorGoal)
	if not self.client.wait_for_result(rospy.Duration(5)):
	    rospy.loginfo('The base failed to rotate.')

    	rospy.sleep(0.1)


    '''
    Find the current base_link position in the map
    http://wiki.ros.org/tf/TfUsingPython
    '''
    def _getCurrentPosition(self):
	
	_position = []
	_orientation = []

	rospy.loginfo('Waiting for tf listener...')
	transformListenerReady = False
	while not transformListenerReady:
	    try:
		# Determines that most recent time for which Transformer can compute the transform
		# between the two given frames. Returns a rospy.Time.
		if self.tfListener.frameExists("/base_footprint") and self.tfListener.frameExists("/map"):
		    rostime = self.tfListener.getLatestCommonTime('/map', '/base_footprint')

		    # Returns the transform from source_frame to target_frame at time.
		    # time is a rospy.Time.
		    # The transform is returned as position (x,y,z) and an orientation quaternion (x,y,z,w).
		    _position, _orientation = self.tfListener.lookupTransform('/map', '/base_footprint', rostime)

		    rospy.loginfo(_position)
		    rospy.loginfo(_orientation)

		    transformListenerReady = True
	    except tf.Exception:
		rospy.loginfo('tf listener not ready.')
		rospy.sleep(1)

  	rospy.loginfo('tf listener is ready.')
	
	return _position, _orientation



if __name__ == '__main__':
    node = AutonomousPatrol()
    try:
	node.run()
    except rospy.ROSInterruptException:
	node.stop()

