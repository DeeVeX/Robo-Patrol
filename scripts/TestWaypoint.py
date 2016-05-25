from robopatrol.DAO.WaypointDao import WaypointDao
import rospy
import datetime
import json
from time import time
from robopatrol.Control.AutonomousPatrol import AutonomousPatrol

rospy.init_node("TestWaypoint", anonymous=False)

auto_patrol = AutonomousPatrol()
print auto_patrol.move_the_base(2, 1)