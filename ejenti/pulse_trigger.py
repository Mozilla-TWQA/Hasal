#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Usage:
  pulse_trigger.py [--config=<str>] [--cmd-config=<str>] [--server-job-config=<str>] [--clean] [--skip-first-query]
  pulse_trigger.py (-h | --help)

Options:
  -h --help                       Show this screen.
  --config=<str>                  Specify the trigger_config.json file path. [default: configs/ejenti/trigger_config.json]
  --cmd-config=<str>              Specify the cmd_config.json file path. [default: configs/ejenti/cmd_config.json]
  --server-job-config=<str>      Specify the server_job_config.json file path. [default: configs/ejenti/server_job_config.json]
  --clean                         Clean Pulse Queue on Pulse service. [default: False]
  --skip-first-query              Skip first time query of Perfherder/Archive server. [default: False]
"""

import os
import time
import logging
import importlib
from docopt import docopt
from apscheduler.schedulers.background import BackgroundScheduler

from lib.common.commonUtil import CommonUtil
from pulse_modules.tasksTrigger import TasksTrigger
from jobs.status_json_creator import status_json_creator


class LogFilter(logging.Filter):
    def filter(self, record):
        return ''


def main():
    """
    Demo of pushing MetaTask to Pulse.
    It will load Pulse config from `--config`, please create the config json file before run this demo.

    The timestamp file of each job will be stored into "ejenti/pulse_modules/.md5/<JOB_NAME>".

    ex:
    {
        "pulse_username": "<PULSE_USERNAME>",
        "pulse_password": "<PULSE_PASSWORD>"
    }

    Also, you can monitor the Pulse Message Queue from https://pulseguardian.mozilla.org/ website.
    """
    default_log_format = '%(asctime)s %(levelname)s [%(name)s.%(funcName)s] %(message)s'
    default_datefmt = '%Y-%m-%d %H:%M'
    logging.basicConfig(level=logging.INFO, format=default_log_format, datefmt=default_datefmt)

    # loading docopt
    arguments = docopt(__doc__)

    # loading config
    config_arg = arguments['--config']
    config_file = os.path.abspath(config_arg)
    config = CommonUtil.load_json_file(config_file)
    if not config:
        logging.error('There is not trigger config. (Loaded from {})'.format(config_file))
        exit(1)

    # filter the logger
    log_filter = LogFilter()
    for disabled_logger in config.get('log_filter', []):
        logging.getLogger(disabled_logger).addFilter(log_filter)

    # loading cmd_config
    cmd_config_arg = arguments['--cmd-config']
    cmd_config_file = os.path.abspath(cmd_config_arg)
    command_config = CommonUtil.load_json_file(cmd_config_file)
    if not command_config:
        logging.error('There is not command config. (Loaded from {})'.format(cmd_config_file))
        exit(1)

    # loading server job config
    server_job_config_arg = arguments['--server-job-config']
    server_job_config_file = os.path.abspath(server_job_config_arg)
    server_job_config = CommonUtil.load_json_file(server_job_config_file)
    if not server_job_config:
        logging.warn('There is no server job config included. So, there will be no server job, but trigger will still go on. (Loaded from {})'.format(server_job_config_file))

    clean_flag = arguments['--clean']
    skip_first_query_flag = arguments['--skip-first-query']

    try:
        #
        # The `status_json_creator()` for upload Trigger Builds Status
        #
        outside_scheduler = BackgroundScheduler()
        outside_scheduler.start()

        # create Status GIST upload job
        KEY_CONFIG_GIST_USER_NAME = 'gist_user_name'
        KEY_CONFIG_GIST_AUTH_TOKEN = 'gist_auth_token'
        INTERVAL_MINUTES = 30
        gist_user_name = config.get(KEY_CONFIG_GIST_USER_NAME)
        gist_auth_token = config.get(KEY_CONFIG_GIST_AUTH_TOKEN)
        if gist_user_name and gist_auth_token:
            gist_upload_config = {
                'configs': {
                    'gist_user_name': gist_user_name,
                    'gist_auth_token': gist_auth_token
                }
            }
            outside_scheduler.add_job(func=status_json_creator,
                                      trigger='interval',
                                      id='status_gist_uploader',
                                      max_instances=1,
                                      minutes=INTERVAL_MINUTES,
                                      args=[],
                                      kwargs=gist_upload_config)
            logging.info('Enable Status JSON Creator and GIST Uploader.')
        else:
            logging.warn('Please config your GIST user name and auth token to enable Status JSON Creator and GIST Uploader.')

        #
        # load scheduler server jobs
        #
        for job_name, job_detail in server_job_config.items():
            logging.info('Server Job [{}] loading ...'.format(job_name))

            enable = job_detail.get('default-loaded', False)
            if enable:
                try:
                    module_path = job_detail.get('module-path')
                    class_name = job_detail.get('class-name')
                    interval_min = job_detail.get('interval-min', 1)
                    max_instance = job_detail.get('max-instances', 1)
                    parameters = job_detail.get('parameters', {})

                    loaded_module = importlib.import_module(module_path)
                    loaded_class = getattr(loaded_module, class_name)
                    loaded_instance = loaded_class()
                    func_pointer = loaded_instance.run
                    # TODO: currently, the trigger type is only interval
                    outside_scheduler.add_job(func=func_pointer,
                                              trigger='interval',
                                              id=job_name,
                                              max_instances=max_instance,
                                              minutes=interval_min,
                                              args=[],
                                              kwargs=parameters)
                except Exception as e:
                    logging.error(e)
            else:
                logging.info('Disabled')

            logging.info('Server Job [{}] loading done.'.format(job_name))

        #
        # Pulse Trigger
        #
        trigger = TasksTrigger(config=config, cmd_config_obj=command_config, clean_at_begin=clean_flag)
        trigger.run(skip_first_query=skip_first_query_flag)

        while True:
            time.sleep(10)
    except Exception as e:
        logging.error(e)
        exit(1)


if __name__ == '__main__':
    main()
