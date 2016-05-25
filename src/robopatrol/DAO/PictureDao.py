import requests
from requests.exceptions import ConnectionError
import json
from jsonschema import validate, ValidationError
from time import time
import base64
import cv2
import datetime


class PictureDao:

    configURL = 'http://localhost:9998/pictures'

    def __init__(self):
        pass

    def post_picture(self, image):
        headers = {'Content-type': 'application/json'}
        response = None

        picture = dict()
        timestamp = time()
        timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')

        picture["name"] = timestamp + ".jpeg"
        cnt = cv2.imencode('.jpeg', image)[1].tostring()
        b64 = base64.b64encode(cnt)
        picture["image"] = "data:image/jpeg;base64," + b64

        try:
            requests.post(self.configURL, data=json.dumps(picture), headers=headers)
            response = True
        except ConnectionError:
            response = False

        return response
