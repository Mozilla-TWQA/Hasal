import os
import socket
import psutil
import logging
import datetime
from lib.common.statusFileCreator import StatusFileCreator
from slack_bot import generate_slack_sending_message


DEFAULT_VERIFY_KWARGS_LIST = ['sync_queue', 'async_queue', 'slack_sending_queue', 'configs']

DEFAULT_LINE = '=' * 20

SLACK_LOGGING_LEVEL_INFO = '*[INFO]*'
SLACK_LOGGING_LEVEL_WARN = '*[WARN]*'
SLACK_LOGGING_LEVEL_ERROR = '*[ERROR]*'

DEFAULT_ALERT_USAGE_PERCENT = 70
DEFAULT_AUTO_CLEAN_UP_FLAG = True
DEFAULT_AUTO_CLEAN_UP_KEEP_DATA_PERIOD = 3
KEY_ALERT_USAGE_PERCENT = 'alert_usage_percent'
KEY_AUTO_CLEAN_UP_FLAG = 'auto_clean_up'
KEY_AUTO_CLEAN_UP_KEEP_DATA_PERIOD = 'auto_clean_up_keep_data_period'
KEY_REMOVE_HASAL_OUTPUT_CMD = 'REMOVE-hasal-output'


def verify_consumer_kwargs(kwargs):
    for verify_kwargs_key in DEFAULT_VERIFY_KWARGS_LIST:
        if verify_kwargs_key not in kwargs:
            raise Exception("The current input consumer kwargs didn't contain the kwarg [%s]" % verify_kwargs_key)


def init_consumer(kwargs):
    """
    verify kwargs
    """
    verify_consumer_kwargs(kwargs)


def monitor_system_info(**kwargs):
    """
    [Job Entry Point]
    Monitor the monitor_disk_usage, and report it.
    @return:
    """
    init_consumer(kwargs)

    # create job id folder
    job_id = StatusFileCreator.create_job_id_folder(StatusFileCreator.STATUS_TAG_SYSTEM_INFO_MONITOR)
    job_id_fp = os.path.join(StatusFileCreator.get_status_folder(), job_id)

    # get Slack Sending queue
    sending_queue = kwargs.get('slack_sending_queue')

    # prepare configs
    configs = kwargs.get('configs')

    # get sync queue
    sync_queue = kwargs.get('sync_queue')

    # get cmd settings
    cmd_setting = kwargs.get('cmd_config')

    # checking disk usage
    check_disk_usage(sending_queue=sending_queue, configs=configs, job_id=job_id, job_id_fp=job_id_fp, cmd_setting=cmd_setting, sync_queue=sync_queue)

    # get current host name
    current_host_name = socket.gethostname()
    StatusFileCreator.create_status_file(job_id_fp, StatusFileCreator.STATUS_TAG_GET_HOST_NAME, 900,
                                         current_host_name)

    # get current host ip
    current_host_ip = socket.gethostbyname(current_host_name)
    StatusFileCreator.create_status_file(job_id_fp, StatusFileCreator.STATUS_TAG_GET_HOST_IP, 900,
                                         current_host_ip)


def check_disk_usage(sending_queue, configs, job_id, job_id_fp, cmd_setting, sync_queue):
    """
    Sending alert if the disk usage exceed the alert percent.
    @param sending_queue:
    @param configs:
    @return:
    """
    alert_usage_percent = float(configs.get(KEY_ALERT_USAGE_PERCENT, DEFAULT_ALERT_USAGE_PERCENT))
    auto_clean_up_flag = configs.get(KEY_AUTO_CLEAN_UP_FLAG, DEFAULT_AUTO_CLEAN_UP_FLAG)
    auto_clean_up_data_keep_period = int(configs.get(KEY_AUTO_CLEAN_UP_KEEP_DATA_PERIOD, DEFAULT_AUTO_CLEAN_UP_KEEP_DATA_PERIOD))
    disk_usage = psutil.disk_usage(os.path.abspath(os.sep))
    current_percent = disk_usage.percent

    # create status file after get the current disk usage
    StatusFileCreator.create_status_file(job_id_fp, StatusFileCreator.STATUS_TAG_DISK_USAGE_MONITOR, 900, current_percent)

    if current_percent > alert_usage_percent:
        # current usage percent more than alert setting
        msg = 'Current disk usage is *{percent}%* ({used}/{total} bytes), exceed {alert}%.'.format(percent=current_percent,
                                                                                                   used=disk_usage.used,
                                                                                                   total=disk_usage.total,
                                                                                                   alert=alert_usage_percent)

        logging.warn(msg)

        slack_msg = '{level} {msg}\n*[Time]* {time}\n{line}'.format(level=SLACK_LOGGING_LEVEL_WARN,
                                                                    msg=msg,
                                                                    time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                    line=DEFAULT_LINE)
        # sending to slack sending queue
        msg_obj = generate_slack_sending_message(slack_msg)

        check_sending_queue(sending_queue=sending_queue)
        sending_queue.put(msg_obj)

        # auto clean up action
        if auto_clean_up_flag:

            # get remove hasal cmd obj
            remove_hasal_output_cmd_obj = cmd_setting['cmd-settings'][KEY_REMOVE_HASAL_OUTPUT_CMD]

            # add remove date in cmd config
            # generate keep data date period
            current_utc_time = datetime.datetime.utcnow()
            outdated_date = current_utc_time - datetime.timedelta(days=auto_clean_up_data_keep_period)
            remove_hasal_output_cmd_obj['configs']['date'] = outdated_date.strftime('%Y-%m-%d')

            # generate task obj for sync queue
            task_obj = {"job_id": job_id, "cmd_obj": remove_hasal_output_cmd_obj, "cmd_pattern": KEY_REMOVE_HASAL_OUTPUT_CMD, "input_cmd_str": KEY_REMOVE_HASAL_OUTPUT_CMD}

            # put task obj into queue
            sync_queue.put(task_obj)


def check_sending_queue(sending_queue):
    """
    if the queue is full, then get one item from queue
    """
    if sending_queue.full():
        message_item = sending_queue.get()
        logging.error('The Slack Sending Queue is full, pop one item.\n{line}\n{obj}\n{line}\n'.format(line=DEFAULT_LINE,
                                                                                                       obj=message_item))
