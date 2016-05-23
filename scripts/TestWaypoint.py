from robopatrol.DAO.WaypointDao import WaypointDao
import rospy
from robopatrol.Control.AutonomousPatrol import AutonomousPatrol

rospy.init_node("TestWaypoint", anonymous=False)

waypoint = WaypointDao()
JData = waypoint.get_waypoints()
print(JData)

auto_patrol = AutonomousPatrol()
print auto_patrol.move_the_base(JData[0]["x"], JData[0]["y"])