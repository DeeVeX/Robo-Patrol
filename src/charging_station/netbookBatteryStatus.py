#!/usr/bin/env python


# Robo-Patrol: check battery status of the netbook

import rospy
import roslib
from smart_battery_msgs.msg import SmartBatteryStatus    # needed for the netbook battery

class BatteryStatus():

    lowNetbookBattery = False
    netbookPreviousBatteryLevel = 100

    def __init__(self):
        rospy.init_node('batteryStatus')
	
	# monitor Kobuki's power and charging status if an event occurs (low battery, charging, not charging) 
	rospy.Subscriber("/mobile_base/sensors/core",SensorState,self.sensorPowerEventCallback)

	# monitor netbook's battery power
	rospy.Subscriber("/laptop_charge/",SmartBatteryStatus,self.netbookPowerEventCallback)
	

    def batteryLevel(self,data):
	# has the netbook's power level changed?
	if (int(data.percentage) != netbookPreviousBatteryLevel):
	    rospy.loginfo("Notebook's battery is now: " + str(data.percentage) + "%")
	    netbookPreviousBatteryLevel = int(data.percentage)

	return netbookPreviousBatteryLevel


	def batteryStatus(self, data):
	# is the netbook's power low?
	if (int(data.percentage) < 25):
            lowNetbookBattery = True
	elif (int(data.percentage) > 35):
	    # the logic of not using the same value (e.g. 25) for both the battery is low & battery is fine is that it'll leave and
            # immediatly return for more power.
	    lowNetbookBattery = False

	return lowNetbookBattery