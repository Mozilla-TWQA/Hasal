import logging
import importlib


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
        func_point = getattr(importlib.import_module(current_queue_msg['cmd_obj']['module-path']),
                             current_queue_msg['cmd_obj']['func-name'])
        func_point(consumer_config=kwargs['configs'], queue_msg=current_queue_msg, slack_sending_queue=slack_sending_queue)


def async_tasks_consumer(**kwargs):
    init_consumer(kwargs)
    async_queue = kwargs['async_queue']
    slack_sending_queue = kwargs.get('slack_sending_queue')
    if async_queue.qsize() > 0:
        current_queue_msg = async_queue.get()
        logging.debug("Get a new queue msg [%s] from async_queue" % current_queue_msg)
        func_point = getattr(importlib.import_module(current_queue_msg['cmd_obj']['module-path']),
                             current_queue_msg['cmd_obj']['func-name'])
        func_point(consumer_config=kwargs['configs'], queue_msg=current_queue_msg, slack_sending_queue=slack_sending_queue)
