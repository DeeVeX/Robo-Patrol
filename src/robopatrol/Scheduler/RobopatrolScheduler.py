from apscheduler.schedulers.background import BackgroundScheduler
import re
import copy


class RobopatrolScheduler(BackgroundScheduler):

    # TODO: Make better validation
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

    def __init__(self, job_listdict):
        BackgroundScheduler.__init__(self)
        self.job_listdict = job_listdict
        self.__add_jobs_by_dict(job_listdict)

    def __parse_cron(self, cron_string):
        validated_cron = self.validate_crontab.match(cron_string)
        if validated_cron is not None:
            return validated_cron.groupdict()
        else:
            return None

    def __edit_jobdict(self, jobname=None, cron=None):
        if jobname is not None and cron is not None:
            for job in self.job_listdict:
                if job['name'].__name__ == jobname:
                    job['cron'] = cron

    def __add_jobs_by_dict(self, job_listdict):
        for job_dict in job_listdict:
            crondict = self.__parse_cron(job_dict['cron'])
            if crondict is None:
                job_listdict.remove(job_dict)
                continue
            try:
                func = job_dict['name']
            except KeyError:
                print "Could not find function: " + job_dict['name'] + ". You have to define this one."
                job_listdict.remove(job_dict)
                continue

            self.add_job(func, name=func.__name__, trigger='cron',
                         second=crondict['second'],
                         minute=crondict['minute'],
                         hour=crondict['hour'],
                         day=crondict['day'],
                         month=crondict['month'],
                         day_of_week=crondict['day_of_week'])

    def reschedule_by_cron(self, job, cron):
        crondict = self.__parse_cron(cron)
        if crondict is not None:
            self.__edit_jobdict(job.name, cron)
            job.reschedule('cron',
                           second=crondict['second'],
                           minute=crondict['minute'],
                           hour=crondict['hour'],
                           day=crondict['day'],
                           month=crondict['month'],
                           day_of_week=crondict['day_of_week'])

    def get_job_by_name(self, scheduler, job_name):
        job_list = scheduler.get_jobs()
        return next((x for x in job_list if x.name == job_name), None)

    def get_jobs_json(self):
        jobs_json = copy.deepcopy(self.job_listdict)
        for job_dict in jobs_json:
            job_dict['name'] = job_dict['name'].__name__
        return jobs_json

    def pause_all_jobs(self):
        for job in self.get_jobs():
            job.pause()
