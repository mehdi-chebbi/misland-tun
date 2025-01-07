import django_rq
import redis
from django_rq import get_worker
import os
from django.conf import settings
import datetime

# from ldms.tasks import add_numbers

# http://peter-hoffmann.com/2012/python-simple-queue-redis-queue.html
# https://levelup.gitconnected.com/unleashing-the-power-of-redis-x-django-1c84b716679b
# https://github.com/rq/django-rq
# https://spapas.github.io/2015/01/27/async-tasks-with-django-rq/
# https://spapas.github.io/2015/09/01/django-rq-redux/

# class RedisQueue(object):
#     """Simple queue with Redis Backend"""
#     def __init__(self, name, namespace='queue', **redis_kwargs):
#         """
#         The default connection parameters are host='localhost', port=6379, db=0
#         """
#         self.__db = redis.Redis(**redis_kwargs)
#         self.key = '%s:%s' % (namespace, name)

#     def qsize(self):
#         """Return size of the queue"""
#         return self.__db.llen(self.key)

#     def is_empty(self):
#         """Return True if queue is empty"""
#         return self.qsize() == 0

#     def put(self, item):
#         """Put item into the queue"""
#         self.__db.rpush(self.key)

class RedisQueue(object):
    """
    Simple queue to handle processing tasks    
    """
    def __init__(self): #, args, **kwargs):
        # self.__redis_cursor = redis.StrictRedis(host='', port='', db='', password='') 
        # redis_cursor = redis.StrictRedis(host='', port='', db='', password='')
        # self.high_queue = django_rq.get('high', connection=redis_cursor)
        # self.low_queue = django_rq.get('low', connection=redis_cursor)
        self.job_timeout = settings.JOB_TIMEOUT# os.getenv('QUEUED_JOB_TIMEOUT', 10800) # default to 3 hours

    def enqueue(self, func, *args, **kwargs):
        """
        Queue task to the default duration queue
        """
        self.enqueue_medium(func, *args, **kwargs)

    def enqueue_extra_high(self, func, *args, **kwargs):
        """
        Queue task to the extra high duration queue
        """
        queue = self._get_queue('extra_high')
        self._enqueue(queue, func, *args, **kwargs)

    def enqueue_high(self, func, *args, **kwargs):
        """
        Queue task to the high duration queue
        """
        queue = self._get_queue('high')
        self._enqueue(queue, func, *args, **kwargs)

    def enqueue_low(self, func, *args, **kwargs):
        """
        Queue task to the low duration queue
        """
        queue = self._get_queue('low')
        self._enqueue(queue, func, *args, **kwargs)

    def enqueue_medium(self, func, *args, **kwargs):
        """
        Queue task to the medium duration queue
        """        
        queue = self._get_queue('default')
        self._enqueue(queue, func, *args, **kwargs)        

    def _enqueue(self, queue, func, *args, **kwargs):
        """
        Queue task
        """
        # print("Job timeout: ", self.job_timeout)
        print ("Enqueuing...{0}. Job timeout={1}".format(datetime.datetime.now(), self.job_timeout))
        queue.enqueue(func, *args, **kwargs, job_timeout=self.job_timeout)
        print ("Enqueued.." + str(func))

    def _get_queue(self, queue_name):
        """Get queue"""
        return django_rq.get_queue(queue_name, autocommit=True, is_async=True, default_timeout=self.job_timeout)

def job_exception_handler(job, *exc_info):
    # update Scheduled Task with error    
    print("Job exception handler ", *exc_info)
    move_to_failed_queue(job, *exc_info)
    pass 

def move_to_failed_queue(job, *exc_info):
    worker = get_worker(job.origin)
    worker.move_to_failed_queue(job, *exc_info)
    return True

# queue = django_rq.get_queue('default', default_timeout=800)
#     queue.enqueue(add_numbers, args=(13, 6, ))