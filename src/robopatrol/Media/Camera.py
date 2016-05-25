from TakePhoto import TakePhoto
import time
import datetime
import cv2

class Camera:

    def __init__(self):
        self.takePhoto = TakePhoto()

    def get_photo(self):
        return self.takePhoto.take_picture()
