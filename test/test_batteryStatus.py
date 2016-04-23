import unittest
import baseBatteryStatus

class CheckBaseBattery(unittest.TestCase):

    def changingBasePower(self):

        batteryStatus = batteryStatus()
        isCharging = isCharging()
        batteryLevel = batteryLevel()

        # batteryStatus
        self.assertEqual(batteryStatus(20), "Kobuki battery is low")
        self.assertEqual(batteryStatus(20), "Kobuki battery is fine")


        # isCharging
        self.assertEqual(isCharging(0), "Stopped charging")
        self.assertEqual(isCharging(1), "Pumping petrol at the station")


        # batteryLevel
        self.assertEqual(batteryLevel(65), 65)

if __name__ == '__main__':
    unittest.main()