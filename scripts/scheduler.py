from datetime import datetime
import re
import time
import requests
import json
from jsonschema import validate
from jsonschema import ValidationError
from apscheduler.schedulers.background import BackgroundScheduler

#CONFIGURATION
poll_interval_sec = 5
configURL = 'http://localhost:9998/schedule'

schema_job = {
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "cron": {"type": "string"}
    },
    "required": ["id", "name", "cron"]
}
######################################################################################################
#ADD YOUR JOB HERE.
job_listdict = [
    {
        "name": "my_job",
        "description": "Testjob, which tests the scheduler. (Remove as soon as this script is table)",
        "cron": "*/5 * * * * *"
    }#,
#    {
#        "name": "TEMPLATE",
#        "description": "COPY ME ( I AM LE TEMPLATE)",
#        "cron": "* * * * * *"
#    }
]
# END JOB SECTION
######################################################################################################

#######################################################################################################
#CREATE YOUR FUNCTIONS FOR YOUR SCHEDULED JOB
def my_job():
    print('Tick! The time is: %s' % datetime.now())


#SCHEDULER FUNCTION SECTION END
#######################################################################################################


#TODO: Make better validation
validate_crontab = re.compile( \
    "{0}\s+{1}\s+{2}\s+{3}\s+{4}\s+{5}".format( \
        "(?P<second>[^ ]+)", \
        "(?P<minute>[^ ]+)", \
        "(?P<hour>[^ ]+)", \
        "(?P<day>[^ ]+)", \
        "(?P<month>[^ ]+)", \
        "(?P<day_of_week>[^ ]+)" \
        )
)

def get_job_by_name(scheduler, job_name):
    job_list = scheduler.get_jobs()
    return next((x for x in job_list if x.name == job_name), None)


def get_json_dict_job_by_name(json_dict_jobs, job_name):
    return next((job for job in json_dict_jobs if job['name'] == job_name), None)


def pause_all_jobs(scheduler):
    for job in scheduler.get_jobs:
        job.pause()


def parse_cron(cron_string):
    validated_cron = validate_crontab.match(cron_string)
    if validated_cron is not None:
        return validated_cron.groupdict()
    else:
        return None


def add_jobs_by_json(scheduler, job_listdict):
    for job_dict in job_listdict:

        print "cronstring: " + job_dict['cron']
        crondict = parse_cron(job_dict['cron'])
        print "crondict: " + str(crondict)
        if crondict is None:
            job_listdict.remove(job_dict)
            continue

        try:
            func = globals()[job_dict['name']]
        except KeyError:
            print "Could not find function: " + job_dict['name'] +". You have to define this one."
            job_listdict.remove(job_dict)
            continue

        scheduler.add_job(func, name=job_dict['name'], trigger='cron',
                          second=crondict['second'],
                          minute=crondict['minute'],
                          hour=crondict['hour'],
                          day=crondict['day'],
                          month=crondict['month'],
                          day_of_week=crondict['day_of_week'])
    return job_listdict


def post_jobs(job_listdict):
    headers = {'Content-type': 'application/json'}
    myResponse = requests.get(configURL)
    if not myResponse.ok:
        return None
    else:
        JData = json.loads(myResponse.content)
        namelist = [x['name'] for x in JData if 'name' in x]
        for job_dict in job_listdict:
            if job_dict['name'] not in namelist:
                response = requests.post(configURL, data=json.dumps(job_dict), headers=headers)


def reschedule_by_cron(job, cron):
    crondict = parse_cron(cron)
    if crondict is not None:
        job.reschedule('cron',
                       second=crondict['second'],
                       minute=crondict['minute'],
                       hour=crondict['hour'],
                       day=crondict['day'],
                       month=crondict['month'],
                       day_of_week=crondict['day_of_week'])


def terminate(scheduler):
    scheduler.shutdown()


#Initializing stuff
scheduler = BackgroundScheduler()
added_jobs = add_jobs_by_json(scheduler, job_listdict)
posted_jobs = post_jobs(added_jobs)
scheduler.start()

try:
    while True:
        time.sleep(poll_interval_sec)
        print "polling"
        #Preconditions
        try:
            myResponse = requests.get(configURL)
            print "response: " + myResponse.content
            if myResponse.ok:
                JData = json.loads(myResponse.content)
            else:
                pause_all_jobs(scheduler)
        except ValueError:
            pause_all_jobs(scheduler)

        #Pause job if not in configuration db. Reschedule job if interval changed.
        for job in scheduler.get_jobs():
            job_dict = get_json_dict_job_by_name(JData, job.name)
            job_dict_actual = get_json_dict_job_by_name(job_listdict, job.name)
            #Validate JSON content
            try:
                validate(job_dict, schema_job)
            except ValidationError:
                job_dict = None

            #Process actions
            if job_dict is None:
                job.pause()
            else:
                 if job_dict_actual['cron'] != job_dict['cron'] or job.next_run_time is None:
                    print "modifying " + job_dict_actual['cron'] + " to " + job_dict['cron']
                    print "before " + str(job_listdict)
                    job_dict_actual['cron'] = job_dict['cron']
                    print "afterward " + str(job_listdict)
                    reschedule_by_cron(job, job_dict['cron'])

except (KeyboardInterrupt, SystemExit):
    # Not strictly necessary if daemonic mode is enabled but should be done if possible
    terminate(scheduler)

