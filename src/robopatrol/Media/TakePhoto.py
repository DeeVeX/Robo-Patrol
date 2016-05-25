import cv2

from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import rospy


class TakePhoto:
    def __init__(self):

        # rospy.init_node('take_photo', anonymous=False)
        self.bridge = CvBridge()
        self.image_received = False

    def callback(self, data):

        # Convert image to OpenCV format
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        self.image_received = True
        self.image = cv_image

    def take_picture(self):
        # Connect image topic
        img_topic = "/camera/rgb/image_raw"
        self.image_sub = rospy.Subscriber(img_topic, Image, self.callback)
        rospy.sleep(1)

        if self.image_received:
            return self.image
        else:
            return None
