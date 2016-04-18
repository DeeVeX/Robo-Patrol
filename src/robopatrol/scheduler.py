from datetime import datetime
import time
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler

poll_interval_sec = 5
my_job_interval_sec = 3600
my_job_name = 'my_job'
configURL = 'http://192.168.115.1:9998/schedule'

def my_job():
    print('Tick! The time is: %s' % datetime.now())


def get_job_by_name(scheduler, job_name):
    job_list = scheduler.get_jobs()
    return next((x for x in job_list if x.name == job_name), None)


def terminate():
    scheduler.shutdown()

scheduler = BackgroundScheduler()
scheduler.add_job(my_job, 'interval', seconds=my_job_interval_sec, name=my_job_name)
scheduler.start()

job_interval = my_job_interval_sec
try:
    # This is here to simulate application activity (which keeps the main thread alive).
    while True:
        time.sleep(poll_interval_sec)

        myResponse = requests.get(configURL)
        if myResponse.ok:
            JData = json.loads(myResponse.content)
            if int(JData['scheduler_config']['interval_sec']) != job_interval:
                job_name = JData['scheduler_config']['jobname']
                job = get_job_by_name(scheduler, job_name)
                if job is not None:
                    job_interval = int(JData['scheduler_config']['interval_sec'])
                    print 'rescheduling', job_interval
                    scheduler.reschedule_job(job.id, trigger='interval', seconds=job_interval)
                else:
                    terminate()
                    break
        else:
            terminate()
            break


except (KeyboardInterrupt, SystemExit):
    # Not strictly necessary if daemonic mode is enabled but should be done if possible
    terminate()

