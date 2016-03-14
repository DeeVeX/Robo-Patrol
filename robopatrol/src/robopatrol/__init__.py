import rospy
from geometry_msgs.msg import Twist


class RoboPatrol():

    def __init__(self):
        rospy.init_node('robopatrol_move')
        
    	rospy.loginfo("To stop RoboPatrol CTRL + C")

        rospy.on_shutdown(self.shutdown)

        self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)
        
        while not rospy.is_shutdown():
            speed = input("Speed: ")
            distance = input("Distance: ")
            self.move(speed, distance)

    def move(self, speed, distance):
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

        
    def shutdown(self):
        rospy.loginfo("Stop RoboPatrol")
        self.cmd_vel.publish(Twist())
        rospy.sleep(1)

