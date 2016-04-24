import requests
import json
from jsonschema import validate, ValidationError


class ConfigDBDao:

    schema_job = {
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "description": {"type": "string"},
            "cron": {"type": "string"}
        },
        "required": ["id", "name", "cron"]
    }

    configURL = 'http://localhost:9998/schedule'

    def __init__(self):
        pass

    def get_jobs(self):
        myResponse = requests.get(self.configURL)
        try:
            if myResponse.ok:
                JData = json.loads(myResponse.content)
                #Validate and remove invalid
                for job in JData:
                    try:
                        validate(job, self.schema_job)
                    except ValidationError:
                        JData.remove(job)
            else:
                JData = None
        except ValueError:
            JData = None
        return JData

    def get_job(self, name):
        jobs = self.get_jobs()
        job = next((job for job in jobs if job['name'] == name), None)

    def post_jobs(self, job_listdict):
        headers = {'Content-type': 'application/json'}
        myresponse = requests.get(self.configURL)
        response = None

        if myresponse.ok:
            JData = json.loads(myresponse.content)
            namelist = [x['name'] for x in JData if 'name' in x]
            for job_dict in job_listdict:
                if job_dict['name'] not in namelist:
                    response = requests.post(self.configURL, data=json.dumps(job_dict), headers=headers)
        return response
