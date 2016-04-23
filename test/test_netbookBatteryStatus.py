import unittest
import netbookBatteryStatus

class CheckNetbookBattery(unittest.TestCase):

    def changingNetbookPower(self):

        batteryStatus = batteryStatus()
        batteryLevel = batteryLevel()

        # batteryStatus
        self.assertEqual(batteryStatus(20), True)
        self.assertEqual(batteryStatus(50), False)

        # batteryLevel
        self.assertEqual(batteryLevel(65), 65)

if __name__ == '__main__':
    unittest.main()