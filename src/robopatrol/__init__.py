import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import numpy as np
import random
from math import radians


class RoboPatrol():

    def __init__(self):
        """
        Initializes the TurtleBot
        """
        rospy.init_node('robopatrol_move')
        
    	rospy.loginfo("To stop RoboPatrol CTRL + C")

        rospy.on_shutdown(self.shutdown)

        # Publishers and Subscribers
        self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
        self.sub = rospy.Subscriber('scan', LaserScan, self.laser_callback)

        self.closest = 0
        self.position = 0

        mode = raw_input("Select operation mode: a (Autonomous), u (User controlled): ")

        if mode == 'a':
            self.drive_autonomous()
        elif mode == 'u':
            self.drive_user()
        else:
            rospy.loginfo("Invalid input: " + mode)

    def drive_user(self):
        """
        Lets the user drive the TurtleBot. User inputs speed, distance and turn radius
        via command line.
        """
        while not rospy.is_shutdown():
                speed = input("Speed: ")
                distance = input("Distance: ")
                turn = input("Turn: ")
                self.move(speed, distance, turn)


    def move(self, speed, distance, turn):
        """
        Moves the TurtleBot by specified speed, distance and turn angle
        :param speed: the speed in meters / second
        :param distance: the distance it will drive TODO provide unit
        :param turn: the angle it will turn in degrees
        """

        if turn > 0:
            self.turn(turn)

        move_cmd = Twist()
        
        move_cmd.linear.x = speed
        move_cmd.linear.y = 0
        move_cmd.linear.z = 0

        move_cmd.angular.x = 0
        move_cmd.angular.y = 0
        move_cmd.angular.z = 0

        t0 = rospy.rostime.get_time()
        current_distance = 0
        rate = rospy.Rate(100);

        while current_distance < distance:
            self.cmd_vel.publish(move_cmd)
            t1 = rospy.rostime.get_time()
            current_distance = abs(speed * (t1 - t0))
            rate.sleep()

        self.cmd_vel.publish(Twist())


    def turn(self, degree):
        """
        Turns the bot by the given degrees.
        :param degree: by how many degrees the bot should turn
        """
        move_cmd = Twist()
        r = rospy.Rate(5.0)

        move_cmd.linear.x = 0
        move_cmd.linear.y = 0
        move_cmd.linear.z = 0

        move_cmd.angular.x = 0
        move_cmd.angular.y = 0

        yaw_rate = degree / 4
        move_cmd.angular.z = radians(yaw_rate)   # turn with yaw_rate / sec for 4 sec

        for i in range(20):         # 20*5hz = 4sec
            self.cmd_vel.publish(move_cmd)
            r.sleep()

        move_cmd.angular.z = 0
        self.cmd_vel.publish(move_cmd)

        self.cmd_vel.publish(Twist())

    def drive_autonomous(self):
        """
        Lets the TurtleBot drive around by itself, distance and turn radius are
        currently determined randomly.
        """
        rospy.loginfo("Driving by myself")
        speed = 0.3 # meter per seconds
        distance = 0.1
        while not rospy.is_shutdown():
            if self.detect_obstacle():
                self.turn(30)
            else:
                self.move(speed, distance, 0)

    def detect_obstacle(self):
        """
        Returns True if the turtle bot sees an obstacle close ahead
        """
        return self.closest < 0.5

    def laser_callback(self, scan):
        """
        Callback called by the laser pubisher
        :param scan: scan object provided by laser publisher
        """
        self.getPosition(scan)
        #rospy.loginfo("position: {0}" .format(self.position))
        #rospy.loginfo("closest: {0}" .format(self.closest))

    def getPosition(self, scan):
        """
        Determines the TurtleBot's position using the laser scan.
        :param scan: scan object provided by laser publisher
        """
        # Build a depths array to rid ourselves of any nan data inherent in scan.ranges.
        depths = []
        for dist in scan.ranges:
            if not np.isnan(dist):
                depths.append(dist)
        #scan.ranges is a tuple, and we want an array.
        fullDepthsArray = scan.ranges[:]

        #If depths is empty that means we're way too close to an object to get a reading.
        #thus establish our distance/position to nearest object as "0".
        if len(depths) == 0:
            self.closest = 0
            self.position = 0
        else:
            self.closest = min(depths)
            self.position = fullDepthsArray.index(self.closest)
        
    def shutdown(self):
        """
        Stops the Turtlebot.
        """
        rospy.loginfo("Stop RoboPatrol")
        self.cmd_vel.publish(Twist())
        rospy.sleep(1)

