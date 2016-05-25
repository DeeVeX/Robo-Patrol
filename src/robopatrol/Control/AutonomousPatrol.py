import rospy
import actionlib
from actionlib_msgs.msg import *
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Pose, Point, Quaternion, Twist
import nav_msgs.msg
import tf
import math


class AutonomousPatrol():
    __patrolActive = False

    # reference coordinate frame, used in the MoveBaseGoal message
    # base_footprint	attached to the mobile base
    __COORDINATE_FRAME_BASE = 'base_footprint'
    __COORDINATE_FRAME_MAP = 'map'

    # [m]
    __defaultDistanceX = 0.2
    __defaultDistanceY = 0.0

    def __init__(self):

        # method stop is called in case of shutdown or failure
        rospy.on_shutdown(self.stop)

        # Constructs a SimpleActionClient and opens connections to an ActionServer.
        # The move_base package provides an implementation of an action.
        # spawning a new thread
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)

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

        # get current pose from odometry and store it in global variable odomPose
        rospy.Subscriber('odom', nav_msgs.msg.Odometry, self._setCurrentOdomPoseCallback)

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

        for i in range(0, 3):
            pub.publish(twist)
            rospy.sleep(1)

        self.__patrolActive = False
        rospy.loginfo('Robot has stopped.')

    '''
    Starts the autonomous patrol
    '''

    def startAutopatrol(self):

        self.__patrolActive = True

        rospy.loginfo('Starting patrol...')

        # create a goal
        goal = MoveBaseGoal()

        # set coordinate frame
        goal.target_pose.header.frame_id = self.__COORDINATE_FRAME_BASE

        # set time stamp
        goal.target_pose.header.stamp = rospy.Time.now()

        # set the pose (position + orientation)
        goal.target_pose.pose = Pose(Point(self.__defaultDistanceX, self.__defaultDistanceY, 0), Quaternion(0, 0, 0, 1))

        '''
        *************************************************************************************************

        This is the main loop.
        Now for the fun part, the actual exploration!

        *************************************************************************************************
        '''
        while not rospy.is_shutdown():
            self.moveTheBase(goal)

        self.__patrolActive = False

    def isAutopatrolActive(self):
        return self.__patrolActive

    def move_the_base(self, x, y):
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = self.__COORDINATE_FRAME_MAP
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = x
        goal.target_pose.pose.position.y = y
        goal.target_pose.pose.position.z = 0
        goal.target_pose.pose.orientation.x = 0
        goal.target_pose.pose.orientation.y = 0
        goal.target_pose.pose.orientation.z = 0
        goal.target_pose.pose.orientation.w = 1
        return self.moveTheBase(goal)

    '''
    @param   MoveBaseGoal target, int timeout [s]   default value = 30 [s]
             message format: geometry_msgs/PoseStamped target_pose

	     important: especify the coordinate frame when passing the target goal (map, base_footprint, ...)
    @return  boolean     goal reached true or false
    '''

    def moveTheBase(self, target, timeout=30):

        if not rospy.is_shutdown():
            self.client.cancel_goals_at_and_before_time(rospy.Time.now())

        # send the navigation goal to the navigation stack
        self.client.send_goal(target)

        success = self.client.wait_for_result(rospy.Duration(timeout))
        # rospy.loginfo("success -> " + str(success))
        if not success:
            self.client.cancel_goal()
            rospy.loginfo("The base failed to reach the goal.")
        else:
            state = self.client.get_state()
            # rospy.loginfo("state -> " + str(state))
            if state == GoalStatus.SUCCEEDED:
                rospy.loginfo("MoveBaseGoal reached, yay! Team RoboPatrol FTW !")
            # self.printCurrentPosition()

        return success

    '''
    @param   float rad (angle in radians)
    '''

    def rotate(self, rad):

        quaternionDifference = tf.transformations.quaternion_about_axis(rad, (0, 0, 1))
        position, quaternion = self.getCurrentMapPosition()

        transformedQuaternion = tf.transformations.quaternion_multiply(quaternion, quaternionDifference)

        if not rospy.is_shutdown():
            self.client.cancel_goals_at_and_before_time(rospy.Time.now())

        rotatorGoal = MoveBaseGoal()
        # set coordinate frame
        rotatorGoal.target_pose.header.frame_id = self.__COORDINATE_FRAME_BASE
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

        rospy.sleep(1)

    '''
    Returns the current position of the base relative to the map
    http://wiki.ros.org/tf/TfUsingPython
    '''

    def getCurrentMapPosition(self):

        _position = []
        _orientation = []

        if not rospy.is_shutdown():
            # Waiting for tf listener...
            transformListenerReady = False
            while not transformListenerReady:
                try:
                    # Determines that most recent time for which Transformer can compute the transform
                    # between the two given frames. Returns a rospy.Time.
                    if self.tfListener.frameExists("/base_footprint") and self.tfListener.frameExists("/map"):
                        rostime = self.tfListener.getLatestCommonTime('/map', '/base_footprint')

                        # Returns the transform from source_frame to target_frame at time.
                        # lookupTransform(target_frame, source_frame, time) -> position, quaternion
                        # time is a rospy.Time.
                        # The transform is returned as position (x,y,z) and an orientation quaternion (x,y,z,w).
                        _position, _orientation = self.tfListener.lookupTransform('/map', '/base_footprint', rostime)
                        transformListenerReady = True
                except tf.Exception:
                    # tf listener is not ready
                    rospy.sleep(1)

        return _position, _orientation

    def printCurrentPosition(self):

        pos, quat = self.getCurrentMapPosition()
        rospy.loginfo("current position (x,y,z) -> " + str(pos))
        rospy.loginfo("current orientation (x,y,z,w) -> " + str(quat))

    '''
    ***** TESTS *****
    '''

    def runAllTests(self):

        pos, quat = self.getCurrentMapPosition()

        self.testMoveToMapPosition([-2, 0, 0], [0, 0, 0, 1])

        self.testBaseHasMoved(pos)

        self.testMoveForwardOneMetre()

        self.testStayStill()

        # random move base test
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = self.__COORDINATE_FRAME_BASE
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = 3
        goal.target_pose.pose.position.y = 0
        goal.target_pose.pose.position.z = 0
        goal.target_pose.pose.orientation.x = 0
        goal.target_pose.pose.orientation.y = 0
        goal.target_pose.pose.orientation.z = 0
        goal.target_pose.pose.orientation.w = 1
        self.moveTheBase(goal)

    def testStayStill(self):

        rospy.loginfo('Test: stay still')

        if not rospy.is_shutdown():
            self.client.cancel_goals_at_and_before_time(rospy.Time.now())

        # estimated position
        self.printCurrentPosition()

        pos, quat = self.getCurrentMapPosition()

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = self.__COORDINATE_FRAME_BASE
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = pos[0]
        goal.target_pose.pose.position.y = pos[1]
        goal.target_pose.pose.position.z = pos[2]
        goal.target_pose.pose.orientation.x = quat[0]
        goal.target_pose.pose.orientation.y = quat[1]
        goal.target_pose.pose.orientation.z = quat[2]
        goal.target_pose.pose.orientation.w = quat[3]

        self.client.send_goal(goal)
        self.client.wait_for_result(rospy.Duration(30))

        newPos, newQuat = self.getCurrentMapPosition()
        rospy.loginfo("startPosition x -> " + str(pos[0]) + ", newPosition x -> " + str(newPos[0]))
        rospy.loginfo("startPosition y -> " + str(pos[1]) + ", newPosition y -> " + str(newPos[1]))

        rospy.loginfo("assertion = " + str(self.almostEqual(pos[0], newPos[0], 1)))
        rospy.loginfo("assertion = " + str(self.almostEqual(pos[1], newPos[1], 1)))

    def testMoveForwardOneMetre(self):

        rospy.loginfo('Test: move forward one metre')

        if not rospy.is_shutdown():
            self.client.cancel_goals_at_and_before_time(rospy.Time.now())

        self.printCurrentPosition()

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = self.__COORDINATE_FRAME_BASE
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose = Pose(Point(1, 0, 0), Quaternion(0, 0, 0, 1))

        self.client.send_goal(goal)
        self.client.wait_for_result(rospy.Duration(30))

        self.printCurrentPosition()

    '''
    @param 	int[] startPosition (3d vector)
    '''

    def testBaseHasMoved(self, startPosition):

        rospy.loginfo('Test: base has moved')

        self.printCurrentPosition()

        pos, quat = self.getCurrentMapPosition()

    # assert startPosition[0] != pos[0]
    # assert startPosition[1] != pos[1]


    '''
    @param 	int[] pos (3d vector) 		= POSIION
		int[] quaternion (4d vector)	= ORIENTATION
    '''

    def testMoveToMapPosition(self, point, quaternion):

        rospy.loginfo('Test: move to position on map')

        if not rospy.is_shutdown():
            self.client.cancel_goals_at_and_before_time(rospy.Time.now())

        self.printCurrentPosition()

        pos, quaternion = self.getCurrentMapPosition()

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = self.__COORDINATE_FRAME_MAP
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = pos[0]
        goal.target_pose.pose.position.y = pos[1]
        goal.target_pose.pose.position.z = pos[2]
        goal.target_pose.pose.orientation.x = quaternion[0]
        goal.target_pose.pose.orientation.y = quaternion[1]
        goal.target_pose.pose.orientation.z = quaternion[2]
        goal.target_pose.pose.orientation.w = quaternion[3]

        self.moveTheBase(goal)

        newPos, newQuat = self.getCurrentMapPosition()
        rospy.loginfo("targetPosition x -> " + str(pos[0]) + ", actualPosition x -> " + str(newPos[0]))
        rospy.loginfo("targetPosition y -> " + str(pos[1]) + ", actualPosition y -> " + str(newPos[1]))

        rospy.loginfo("assertion = " + str(self.almostEqual(point[0], newPos[0], 1)))
        rospy.loginfo("assertion = " + str(self.almostEqual(point[1], newPos[1], 1)))

    def almostEqual(self, a, b, digits):
        epsilon = 10 ** -digits
        return abs(a / b - 1) < epsilon
