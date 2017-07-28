import sys
import pickle
import platform
import logging
from modules.hasal_consumer import HasalConsumer


PULSE_KEY_TASK = 'task'
DEFAULT_VERIFY_KWARGS_LIST = ["sync_queue", "async_queue", "configs"]


def verify_consumer_kwargs(kwargs):
    for verify_kwargs_key in DEFAULT_VERIFY_KWARGS_LIST:
        if verify_kwargs_key not in kwargs:
            raise Exception("The current input consumer kwargs didn't contain the kwarg [%s]" % verify_kwargs_key)


def init_consumer(kwargs):
    # verify kwargs
    verify_consumer_kwargs(kwargs)


def get_topic():
    """
    Getting the pulse topic base on local agent's platform.
    @return: topic string base on platform. ex: 'win7', 'win10', 'darwin', 'linux2'. Raise Exception if not supported.
    """
    platform_name = sys.platform

    if 'win32' == platform_name:
        # Windows will have 'win7' and 'win10'
        platform_release = platform.release()
        if '10' == platform_release:
            return 'win10'
        elif '7' == platform_release:
            return 'win7'
        else:
            raise Exception('Does not support this Windows Release: {}'.format(platform_release))
    else:
        # 'darwin' and 'linux2'
        return platform_name


def listen_pulse(**kwargs):
    """
    Listen the message on Pulse.
    It will load the 'configs' from kwargs, and then get 'username' and 'password' from 'configs'.
    Please setting them up in job_config.json.

    ex:
    "listen_pulse": {
        "module-path": "jobs.pulse",
        "trigger-type": "interval",
        "interval": 0,
        "max-instances": 1,
        "default-loaded": true,
        "configs":{
            "username": "<PULSE_USERNAME>",
            "password": "<PULSE_PASSWORD>"
    }
    """
    init_consumer(kwargs)

    # prepare username, password, and label
    configs = kwargs.get('configs')
    username = configs.get('username')
    password = configs.get('password')
    topic = get_topic()
    consumer_label = topic

    async_queue = kwargs.get('async_queue')

    # define the callback
    def got_msg(body, message):
        # handle the message
        # ack then broker will remove this message from queue
        message.ack()

        logging.debug('\n{line}\n### Pulse got message###\nBody:\n{b}\nMessage:\n{m}\n{line}'.format(b=body,
                                                                                                     m=message,
                                                                                                     line='-' * 20))

        data_payload = body.get('payload')
        data = data_payload.get(PULSE_KEY_TASK)
        data_obj = pickle.loads(data)

        # push task into queue
        task_obj = data_obj.get_cmd()
        async_queue.put(task_obj)

    c = HasalConsumer(user=username, password=password, applabel=consumer_label)
    c.configure(topic=topic, callback=got_msg)

    c.listen()
