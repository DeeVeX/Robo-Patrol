import requests
from requests.exceptions import ConnectionError
import json
from jsonschema import validate, ValidationError


class WaypointDao:

    schema_waypoint = {
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "x": {"type": "number"},
            "y": {"type": "number"},
            "lastVisited": {"type": "string"}
        },
        "required": ["id", "x", "y"]
    }

    configURL = 'http://localhost:9998/route'

    def __init__(self):
        pass

    def get_waypoints(self):
        try:
            myResponse = requests.get(self.configURL)
            if myResponse.ok:
                JData = json.loads(myResponse.content)
                #Validate and remove invalid
                for waypoint in JData:
                    try:
                        validate(waypoint, self.schema_waypoint)
                    except ValidationError as e:
                        JData.remove(waypoint)
            else:
                JData = None
        except (ValueError, ConnectionError):
            JData = None
        return JData

    def post_job(self, waypoint):
        headers = {'Content-type': 'application/json'}
        response = None
        try:
            print "puttin"
            response = requests.put(self.configURL+"/"+waypoint['id'], data=json.dumps(waypoint), headers=headers)
            print "did the put"
        except ConnectionError:
            response = False
        return response
