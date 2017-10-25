import os
import logging
import importlib
from lib.common.statusFileCreator import StatusFileCreator


DEFAULT_VERIFY_KWARGS_LIST = ["sync_queue", "async_queue", "configs"]


def verify_consumer_kwargs(kwargs):
    for verify_kwargs_key in DEFAULT_VERIFY_KWARGS_LIST:
        if verify_kwargs_key not in kwargs:
            raise Exception("The current input consumer kwargs didn't contain the kwarg [%s]" % verify_kwargs_key)


def init_consumer(kwargs):
    # verify kwargs
    verify_consumer_kwargs(kwargs)


def sync_tasks_consumer(**kwargs):
    init_consumer(kwargs)
    sync_queue = kwargs['sync_queue']
    slack_sending_queue = kwargs.get('slack_sending_queue')
    if sync_queue.qsize() > 0:
        current_queue_msg = sync_queue.get()
        logging.debug("Get a new queue msg [%s] from sync_queue" % current_queue_msg)
        if "job_id" not in current_queue_msg:
            raise Exception("The current queue message didn't include the job_id key, current queue message [%s]" % current_queue_msg)
        else:
            job_id_path = os.path.join(StatusFileCreator.get_status_folder(), current_queue_msg['job_id'])
            StatusFileCreator.create_status_file(job_id_path, StatusFileCreator.STATUS_TAG_SYNC_TASK_CONSUMER, 100, current_queue_msg)
            func_point = getattr(importlib.import_module(current_queue_msg['cmd_obj']['module-path']),
                                 current_queue_msg['cmd_obj']['func-name'])
            func_point(consumer_config=kwargs['configs'], queue_msg=current_queue_msg, slack_sending_queue=slack_sending_queue)
            StatusFileCreator.create_status_file(job_id_path, StatusFileCreator.STATUS_TAG_SYNC_TASK_CONSUMER, 900)


def async_tasks_consumer(**kwargs):
    init_consumer(kwargs)
    async_queue = kwargs['async_queue']
    slack_sending_queue = kwargs.get('slack_sending_queue')
    if async_queue.qsize() > 0:
        current_queue_msg = async_queue.get()
        logging.debug("Get a new queue msg [%s] from async_queue" % current_queue_msg)
        if "job_id" not in current_queue_msg:
            raise Exception("The current queue message didn't include the job_id key, current queue message [%s]" % current_queue_msg)
        else:
            job_id_path = os.path.join(StatusFileCreator.get_status_folder(), current_queue_msg['job_id'])
            StatusFileCreator.create_status_file(job_id_path, StatusFileCreator.STATUS_TAG_ASYNC_TASK_CONSUMER, 100, current_queue_msg)
            func_point = getattr(importlib.import_module(current_queue_msg['cmd_obj']['module-path']),
                                 current_queue_msg['cmd_obj']['func-name'])
            func_point(consumer_config=kwargs['configs'], queue_msg=current_queue_msg, slack_sending_queue=slack_sending_queue)
            StatusFileCreator.create_status_file(job_id_path, StatusFileCreator.STATUS_TAG_ASYNC_TASK_CONSUMER, 900)
