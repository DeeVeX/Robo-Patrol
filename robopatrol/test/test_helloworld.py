import unittest
from robopatrol.helloworld import Greeter

class MyTestCase(unittest.TestCase):
    def test_default_greeting_set(self):
        greeter = Greeter()
        # this test will fail until you change the Greeter to return this expected message
        self.assertEqual(greeter.message, 'Hello world')
        # this test will fail until you change the expected Value to 2
        self.assertEqual(greeter.addOne(1), 2)

