#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Usage:
  pulse_trigger.py [--config=<str>] [--cmd-config=<str>]
  pulse_trigger.py (-h | --help)

Options:
  -h --help                       Show this screen.
  --config=<str>                  Specify the trigger_config.json file path. [default: trigger_config.json]
  --cmd-config=<str>              Specify the cmd_config.json file path. [default: cmd_config.json]
"""

import os
import re
import time
import pickle
import shutil
import logging
import urllib2
import hashlib
import urlparse
from docopt import docopt
from datetime import datetime, timedelta
from mozillapulse.messages.base import GenericMessage
from apscheduler.schedulers.background import BackgroundScheduler

from pulse_modules.hasal_consumer import HasalConsumer
from pulse_modules.hasal_publisher import HasalPublisher
from pulse_modules.syncMetaTasks import SyncMetaTask
from pulse_modules.asyncMetaTasks import AsyncMetaTask
from jobs.pulse import PULSE_KEY_TASK
from lib.common.commonUtil import CommonUtil


class HasalPulsePublisher(object):

    # refer to `get_topic()` method of `jobs.pulse`
    TOPIC_WIN7 = 'win7'
    TOPIC_WIN10 = 'win10'
    TOPIC_DARWAN = 'darwin'
    TOPIC_LINUX2 = 'linux2'

    # the settings key nome inside the cmd_config.json
    COMMAND_SETTINGS = 'cmd-settings'

    # define the basic command settings key name
    COMMAND_SETTING_QUEUE_TYPE = 'queue-type'
    COMMAND_SETTING_QUEUE_TYPE_SYNC = 'sync'
    COMMAND_SETTING_QUEUE_TYPE_ASYNC = 'async'

    # the debug information key name
    DEBUG_QUEUE_TYPE = 'debug_queue_type'
    DEBUG_COMMAND_NAME = 'debug_command_name'
    DEBUG_COMMAND_CONFIG = 'debug_command_config'
    DEBUG_OVERWRITE_COMMAND_CONFIGS = 'debug_overwrite_command_configs'

    def __init__(self, username, password, command_config):
        """
        Hasal Pulse Publisher.
        @param username: the username of Pulse.
        @param password: the password of Pulse.
        @param command_config: the dict object loaded from cmd_config.json.
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        self.username = username
        self.password = password
        self.command_config = command_config

        if self.COMMAND_SETTINGS not in self.command_config:
            raise Exception('The command config was failed.\n{}'.format(self.command_config))
        self.command_config_settings = self.command_config.get(self.COMMAND_SETTINGS)

    def get_meta_task(self, command_name, overwrite_cmd_configs=None):
        """
        Getting Sync or Async MetaTask object.
        @param command_name: the specified command name, which base on cmd_config.json.
        @param overwrite_cmd_configs: overwrite the Command's config.
        @return: SyncMetaTask or AsyncMetaTask object. Return None if there is not valid queue_type.
        """
        if command_name not in self.command_config_settings:
            self.logger.error('Not support command: {}'.format(command_name))
            return None

        command_setting = self.command_config_settings.get(command_name)
        queue_type = command_setting.get(self.COMMAND_SETTING_QUEUE_TYPE, '')

        if queue_type == self.COMMAND_SETTING_QUEUE_TYPE_SYNC:
            meta_task = SyncMetaTask(command_key=command_name,
                                     command_config=self.command_config,
                                     overwrite_cmd_configs=overwrite_cmd_configs)
        elif queue_type == self.COMMAND_SETTING_QUEUE_TYPE_ASYNC:
            meta_task = AsyncMetaTask(command_key=command_name,
                                      command_config=self.command_config,
                                      overwrite_cmd_configs=overwrite_cmd_configs)
        else:
            self.logger.error('Does not support this command: {}, with the queue type: {}'.format(command_name,
                                                                                                  queue_type))
            return None
        return meta_task

    def push_meta_task(self, topic, command_name, overwrite_cmd_configs=None):
        """
        Push MetaTask into Pulse.
        @param topic: The topic channel.
        @param command_name: the specified command name, which base on cmd_config.json.
        @param overwrite_cmd_configs: overwrite the Command's config.
        @return:
        """
        # get MetaTask
        meta_task = self.get_meta_task(command_name, overwrite_cmd_configs=overwrite_cmd_configs)
        if not meta_task:
            self.logger.error('Skip pushing task.')
        pickle_meta_task = pickle.dumps(meta_task)

        # make publisher
        p = HasalPublisher(user=self.username, password=self.password)

        # prepare message
        mymessage = GenericMessage()

        # setup topic
        mymessage.routing_parts.append(topic)

        mymessage.set_data(PULSE_KEY_TASK, pickle_meta_task)
        # for debugging
        mymessage.set_data(self.DEBUG_QUEUE_TYPE, meta_task.queue_type)
        mymessage.set_data(self.DEBUG_COMMAND_NAME, command_name)
        mymessage.set_data(self.DEBUG_COMMAND_CONFIG, self.command_config)
        mymessage.set_data(self.DEBUG_OVERWRITE_COMMAND_CONFIGS, overwrite_cmd_configs)

        # send
        p.publish(mymessage)
        # disconnect
        p.disconnect()


class TasksTrigger(object):
    ARCHIVE_ROOT_URL = 'https://archive.mozilla.org'
    ARCHIVE_LATEST_FOLDER = '/pub/firefox/nightly/latest-mozilla-central/'
    ARCHIVE_LINK_RE_STRING = r'(?<=href=").*?(?=")'

    KEY_CONFIG_PULSE_USER = 'pulse_username'
    KEY_CONFIG_PULSE_PWD = 'pulse_password'
    KEY_CONFIG_JOBS = 'jobs'
    KEY_JOBS_ENABLE = 'enable'
    KEY_JOBS_TOPIC = 'topic'
    KEY_JOBS_PLATFORM_BUILD = 'platform_build'
    KEY_JOBS_INTERVAL_MINUTES = 'interval_minutes'
    KEY_JOBS_CMD = 'cmd'
    KEY_JOBS_CONFIGS = 'configs'

    MD5_HASH_FOLDER = '.md5'

    # filename example: 'firefox-56.0a1.en-US.linux-x86_64.json'
    MATCH_FORMAT = '.{platform_key}.{ext}'

    PLATFORM_MAPPING = {
        'linux32': {
            'key': 'linux-i686',
            'ext': 'tar.bz2'
        },
        'linux64': {
            'key': 'linux-x86_64',
            'ext': 'tar.bz2'
        },
        'mac': {
            'key': 'mac',
            'ext': 'dmg'
        },
        'win32': {
            'key': 'win32',
            'ext': 'zip'
        },
        'win64': {
            'key': 'win64',
            'ext': 'zip',
        }
    }

    def __init__(self, config, cmd_config_obj):
        self.all_config = config
        self.cmd_config_obj = cmd_config_obj

        # get jobs config
        self.jobs_config = config.get(TasksTrigger.KEY_CONFIG_JOBS, {})
        self.pulse_username = config.get(TasksTrigger.KEY_CONFIG_PULSE_USER)
        self.pulse_password = config.get(TasksTrigger.KEY_CONFIG_PULSE_PWD)

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    @staticmethod
    def get_all_latest_files():
        """
        Get all latest files from ARCHIVE server.
        @return: dict object {'<filename>': '<folder/path/with/filename>', ...}
        """
        latest_url = urlparse.urljoin(TasksTrigger.ARCHIVE_ROOT_URL, TasksTrigger.ARCHIVE_LATEST_FOLDER)
        ret_dict = {}
        try:
            res_obj = urllib2.urlopen(latest_url)
            if res_obj.getcode() == 200:
                for line in res_obj.readlines():
                    match = re.search(TasksTrigger.ARCHIVE_LINK_RE_STRING, line)
                    if match:
                        href_link = match.group(0)
                        name = href_link.split('/')[-1]
                        ret_dict[name] = href_link
            else:
                logging.error('Fetch builds failed. Code: {code}, Link: {link}'.format(code=res_obj.getcode(),
                                                                                       link=latest_url))
        except Exception as e:
            logging.error(e)
        return ret_dict

    @staticmethod
    def get_latest_info_json_url(platform):
        """
        Get latest platform build's JSON file URL base on specify platform.
        @param platform: the specify platform. Defined in PLATFORM_MAPPING[<name>]['key'].
        @return: the latest platform build's JSON file URL.
        """
        ext_json = 'json'
        match_endswith_string = TasksTrigger.MATCH_FORMAT.format(platform_key=platform, ext=ext_json)

        # get latest files
        all_files = TasksTrigger.get_all_latest_files()

        # find the matched files base on platform, e.g. "win64.json"
        matched_files = {k: v for k, v in all_files.items() if k.endswith(match_endswith_string)}

        if len(matched_files) >= 1:
            # when get matched files, then get the latest file URL folder path
            matched_filename = sorted(matched_files.keys())[-1]
            ret_url = matched_files.get(matched_filename)
            return urlparse.urljoin(TasksTrigger.ARCHIVE_ROOT_URL, ret_url)
        else:
            logging.error('There is no matched filename endswith "{}".'.format(match_endswith_string))
            return None

    @staticmethod
    def get_remote_md5(url, max_size=1 * 1024 * 1024):
        """
        Get remote resource's MD5 hash string.
        @param url: remote resource URL.
        @param max_size: max download size. default is 1*1024*1024 bytes (1 MB).
        @return: the MD5 hash string (lowercase).
        """
        remote_resource = urllib2.urlopen(url)
        md5_handler = hashlib.md5()
        counter = 0
        while True:
            data = remote_resource.read(1024)
            counter += 1024

            if not data or counter >= max_size:
                break
            md5_handler.update(data)
        return md5_handler.hexdigest()

    @staticmethod
    def get_latest_info_json_md5_hash(platform):
        """
        Get MD5 hash string of latest platform build's JSON file base on specify platform.
        @param platform: the specify platform. Defined in PLATFORM_MAPPING[<name>]['key'].
        @return: the MD5 hash string of latest platform build's JSON file.
        """
        json_file_url = TasksTrigger.get_latest_info_json_url(platform)
        hash_string = TasksTrigger.get_remote_md5(json_file_url)
        return hash_string

    @staticmethod
    def check_latest_info_json_md5_changed(job_name, platform):
        """
        @param job_name: the job name which will set as identify name.
        @param platform: the platform archive server.
        @return: True if changed, False if not changed.
        """
        current_file_folder = os.path.dirname(os.path.realpath(__file__))

        md5_folder = os.path.join(current_file_folder, TasksTrigger.MD5_HASH_FOLDER)

        # prepare MD5 folder
        if os.path.exists(md5_folder):
            if not os.path.isdir(md5_folder):
                shutil.rmtree(md5_folder)
                os.makedirs(md5_folder)
        else:
            os.makedirs(md5_folder)

        # get new MD5 hash
        new_hash = TasksTrigger.get_latest_info_json_md5_hash(platform)

        # check MD5 file
        job_md5_file = os.path.join(md5_folder, job_name)
        if os.path.exists(job_md5_file):
            with open(job_md5_file, 'r') as f:
                origin_hash = f.readline()

            if origin_hash == new_hash:
                # no changed
                return False
            else:
                # changed
                logging.info('Job "{}" platform "{}": Latest Hash [{}], Origin Hash: [{}]'.format(job_name,
                                                                                                  platform,
                                                                                                  new_hash,
                                                                                                  origin_hash))
                with open(job_md5_file, 'w') as f:
                    f.write(new_hash)
                return True
            pass
        else:
            # 1st check
            logging.info('Job "{}" platform "{}": Latest Hash [{}], no origin hash.'.format(job_name,
                                                                                            platform,
                                                                                            new_hash))
            with open(job_md5_file, 'w') as f:
                f.write(new_hash)
            return True

    @staticmethod
    def _validate_job_config(job_config):
        """
        Validate the job config. Required keys: topic, platform_build, and cmd.
        @param job_config: job detail config.
        @return: True or False.
        """
        required_keys = [TasksTrigger.KEY_JOBS_TOPIC,
                         TasksTrigger.KEY_JOBS_PLATFORM_BUILD,
                         TasksTrigger.KEY_JOBS_CMD]

        for required_key in required_keys:
            if required_key not in job_config:
                logging.error('There is no required key [{}] in job config.'.format(required_key))
                return False
        return True

    @staticmethod
    def job_adding_dumy_listener(username, password, topic):
        """
        [JOB]
        Adding the Pulse listener for creating Queues on Pulse.
        If there is no Queues listen on topic, the message will disappear TwT.
        @param username: Pulse username.
        @param password: Pulse password.
        @param topic: Topic.
        """
        def got_msg(body, message):
            # does not ack, so broker will keep this message
            logging.debug('do nothing here')
        c = HasalConsumer(user=username, password=password, applabel=topic)
        c.configure(topic=topic, callback=got_msg)
        queue_exist = c.queue_exists()
        if not queue_exist:
            logging.warn('Try to declare queue on Topic [{}]'.format(topic))
            try:
                c._build_consumer()
            except Exception as e:
                logging.error(e)
        queue_exists = c.queue_exists()
        logging.debug('Pulse Queue on Topic [{}] exists ... {}'.format(topic, queue_exists))

    @staticmethod
    def job_pushing_meta_task(username, password, command_config, job_name, topic, platform_build, cmd_name, overwrite_cmd_config=None):
        """
        [JOB]
        Pushing the MetaTask if the remote build's MD5 was changed.
        @param username: Pulse username.
        @param password: Pulse password.
        @param command_config: The overall command config dict object.
        @param job_name: The job name which be defined in trigger_config.json.
        @param topic: The Topic on Pulse. Refer to `get_topic()` method of `jobs.pulse`.
        @param platform_build: The platform on Archive server.
        @param cmd_name: The MetaTask command name.
        @param overwrite_cmd_config: The overwrite command config.
        """
        changed = TasksTrigger.check_latest_info_json_md5_changed(job_name=job_name, platform=platform_build)
        if changed:
            # prepare the topic
            push_topic = topic
            # prepare command name
            command_name = cmd_name
            # Push MetaTask to Pulse
            publisher = HasalPulsePublisher(username=username,
                                            password=password,
                                            command_config=command_config)
            # push meta task
            logging.info('Pushing to Pulse, topic [{topic}], command [{cmd}], cmd_config [{cmd_config}]'.format(
                topic=topic,
                cmd=command_name,
                cmd_config=overwrite_cmd_config
            ))
            publisher.push_meta_task(topic=push_topic,
                                     command_name=command_name,
                                     overwrite_cmd_configs=overwrite_cmd_config)

    def run(self):
        for job_name, job_detail in self.jobs_config.items():
            """
            ex:
            {
                "win7_x64": {
                    "enable": true,
                    "topic": "win7",
                    "platform_build": "win64",
                    "interval_minutes": 10,
                    "cmd": "download-latest-nightly",
                    "configs": {}
                },
                ...
            }
            """
            if not TasksTrigger._validate_job_config(job_detail):
                logging.error('There is not valid job.\n{}: {}\n'.format(job_name, job_detail))

            # have default config
            enable = job_detail.get(TasksTrigger.KEY_JOBS_ENABLE, False)
            interval_minutes = job_detail.get(TasksTrigger.KEY_JOBS_INTERVAL_MINUTES, 10)
            configs = job_detail.get(TasksTrigger.KEY_JOBS_CONFIGS, {})
            # required
            topic = job_detail.get(TasksTrigger.KEY_JOBS_TOPIC)
            platform_build = job_detail.get(TasksTrigger.KEY_JOBS_PLATFORM_BUILD)
            cmd = job_detail.get(TasksTrigger.KEY_JOBS_CMD)

            if enable:
                logging.info('Job [{}] is enabled.'.format(job_name))

                # adding Fake Pulse Listener (without ACK)

                listener_name = '{}_listener'.format(job_name)
                time_ten_seconds_after = datetime.now() + timedelta(seconds=10)
                self.scheduler.add_job(func=TasksTrigger.job_adding_dumy_listener,
                                       trigger='interval',
                                       id=listener_name,
                                       max_instances=1,
                                       start_date=time_ten_seconds_after,
                                       minutes=1,
                                       args=[],
                                       kwargs={'username': self.pulse_username,
                                               'password': self.pulse_password,
                                               'topic': topic})

                # adding Job Trigger
                self.scheduler.add_job(func=TasksTrigger.job_pushing_meta_task,
                                       trigger='interval',
                                       id=job_name,
                                       max_instances=1,
                                       minutes=interval_minutes,
                                       args=[],
                                       kwargs={'username': self.pulse_username,
                                               'password': self.pulse_password,
                                               'command_config': self.cmd_config_obj,
                                               'job_name': job_name,
                                               'topic': topic,
                                               'platform_build': platform_build,
                                               'cmd_name': cmd,
                                               'overwrite_cmd_config': configs})

            else:
                logging.info('Job [{}] is disabled.'.format(job_name))


class LogFilter(logging.Filter):
    def filter(self, record):
        return ''


def main():
    """
    Demo of pushing MetaTask to Pulse.
    It will load Pulse config from `--config`, please create the config json file before run this demo.

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
    config_file = arguments['--config']
    config = CommonUtil.load_json_file(config_file)

    # filter the logger
    log_filter = LogFilter()
    for disabled_logger in config.get('log_filter', []):
        logging.getLogger(disabled_logger).addFilter(log_filter)

    # loading cmd_config
    cmd_config_file = arguments['--cmd-config']
    command_config = CommonUtil.load_json_file(cmd_config_file)
    if not command_config:
        raise Exception('There is not command config. (Loaded from {})'.format(cmd_config_file))

    trigger = TasksTrigger(config=config, cmd_config_obj=command_config)
    trigger.run()

    while True:
        time.sleep(10)


if __name__ == '__main__':
    main()
