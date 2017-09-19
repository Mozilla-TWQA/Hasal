#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Usage:
  pulse_trigger.py --query [--config=<str>] [--cmd-config=<str>]
  pulse_trigger.py --remove [--config=<str>] [--cmd-config=<str>]
  pulse_trigger.py (-h | --help)

Options:
  -h --help                       Show this screen.
  --query                         Query the Trigger Jobs status.
  --remove                        Query the Trigger Jobs status, and the remove the checking file of Trigger Jobs.
  --config=<str>                  Specify the trigger_config.json file path. [default: configs/ejenti/trigger_config.json]
  --cmd-config=<str>              Specify the cmd_config.json file path. [default: configs/ejenti/cmd_config.json]
"""

from __future__ import print_function

import os
import logging
from docopt import docopt

from lib.common.commonUtil import CommonUtil
from pulse_modules.tasksTrigger import TasksTrigger


def main():
    # loading docopt
    arguments = docopt(__doc__)

    # loading config
    config_arg = arguments['--config']
    config_file = os.path.abspath(config_arg)
    config = CommonUtil.load_json_file(config_file)
    if not config:
        logging.error('There is not trigger config. (Loaded from {})'.format(config_file))
        exit(1)

    # loading cmd_config
    trigger_config_arg = arguments['--config']
    trigger_config_file = os.path.abspath(trigger_config_arg)
    trigger_config = CommonUtil.load_json_file(trigger_config_file)
    if not trigger_config:
        logging.error('There is not trigger config. (Loaded from {})'.format(trigger_config_file))
        exit(1)

    is_query = arguments['--query']
    is_remove = arguments['--remove']

    if is_query or is_remove:
        try:
            jobs = trigger_config.get('jobs')

            for job_name, job_obj in sorted(jobs.items()):
                is_enabled = job_obj.get('enable')

                print('Job [{name}]: {status}'.format(name=job_name, status='enabled' if is_enabled else 'disabled'))

                if is_remove and is_enabled:
                    input_value = raw_input('>>> Remove the checking file of Job [{name}] (y/N): '.format(name=job_name))

                    if input_value.lower() == 'y' or input_value.lower() == 'yes':
                        print('    cleaning checking file ... ', end='')
                        ret = TasksTrigger.clean_md5_by_job_name(job_name)
                        if ret:
                            print(' OK')
                        else:
                            print(' Failed')

        except Exception as e:
            logging.error(e)
            exit(1)


if __name__ == '__main__':
    main()
