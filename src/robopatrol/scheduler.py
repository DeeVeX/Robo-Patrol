from datetime import datetime
import time
import requests
import json
from jsonschema import validate
from jsonschema import ValidationError
from apscheduler.schedulers.background import BackgroundScheduler

#CONFIGURATION
poll_interval_sec = 5
configURL = 'http://192.168.1.104:9998/schedule'

'''
schema = {"items": {
    "properties": {
        "jobname": {"type": "string"},
        "attributes": {
            "properties": {
                "interval_sec": {"type": "number"}
            },
            "required": ["interval_sec"]
        }
    },
    "required": ["jobname"]
}
}
'''

schema_job = {
    "properties": {
        "jobname": {"type": "string"},
              "attributes": {
                  "properties": {
                      "interval_sec":{"type": "number"}
                  },
                "required": ["interval_sec"]
              },
    },
    "required": ["jobname"]
}


#CREATE YOUR FUNCTIONS FOR YOUR SCHEDULED JOB
def my_job():
    print('Tick! The time is: %s' % datetime.now())


#SCHEDULER FUNCTION SECTION END

def get_job_by_name(scheduler, job_name):
    job_list = scheduler.get_jobs()
    return next((x for x in job_list if x.name == job_name), None)


def get_json_dict_job_by_name(json_dict_jobs, job_name):
    return next((job for job in JData if job['jobname'] == job_name), None)


def terminate():
    scheduler.shutdown()

scheduler = BackgroundScheduler()
scheduler.start()

#CREATE ADDITIONAL JOBS HERE
job = scheduler.add_job(my_job, trigger='interval', name='my_job')
job.pause()     #Required, as the job would start immediately


#ADDITONAL JOBS SECTION END

try:
    while True:
        time.sleep(poll_interval_sec)

#        myResponse = requests.get(configURL)
#        if myResponse.ok:
#            JData = json.loads(myResponse.content)
        jsoncontent = '[{"jobname": "my_job","attributes": {"interval_sec": 2 }}, {"jobname": "my_job2", "attributes": {"interval_sec": 10}}]'
        try:
            JData = json.loads(jsoncontent)
        except(ValueError):
            continue #Try again. Scheduler won't stop just because the REST Endpoint is not correctly configured.

        #Pause job if not in configuration db. Reschedule job if interval changed.
        for job in scheduler.get_jobs():

            job_dict = get_json_dict_job_by_name(JData, job.name)
            #Validate JSON content
            try:
                validate(job_dict, schema_job)
            except ValidationError:
                job_dict = None

            #Process actions
            if job_dict is None:
                job.pause()
            else:
                job_interval_sec_new = int(job_dict['attributes']['interval_sec'])
                if job.trigger.interval.seconds != job_interval_sec_new or job.next_run_time is None:
                    job.reschedule('interval', seconds=job_interval_sec_new)

except (KeyboardInterrupt, SystemExit):
    # Not strictly necessary if daemonic mode is enabled but should be done if possible
    terminate()

