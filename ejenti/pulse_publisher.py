#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Usage:
  pulse_publisher.py [--config=<str>] [--cmd-config=<str>]
  pulse_publisher.py (-h | --help)

Options:
  -h --help                       Show this screen.
  --config=<str>                  Specify the config.json file path. [default: pulse_config.json]
  --cmd-config=<str>              Specify the cmd_config.json file path. [default: cmd_config.json]
"""
import pickle
import logging
from docopt import docopt
from mozillapulse.messages.base import GenericMessage

from pulse.hasal_publisher import HasalPublisher
from pulse.syncMetaTasks import SyncMetaTask
from pulse.asyncMetaTasks import AsyncMetaTask
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

    def get_meta_task(self, command_name):
        """
        Getting Sync or Async MetaTask object.
        @param command_name: the specified command name, which base on cmd_config.json.
        @return: SyncMetaTask or AsyncMetaTask object. Return None if there is not valid queue_type.
        """
        if command_name not in self.command_config_settings:
            self.logger.error('Not support command: {}'.format(command_name))
            return None

        command_setting = self.command_config_settings.get(command_name)
        queue_type = command_setting.get(self.COMMAND_SETTING_QUEUE_TYPE, '')
        if queue_type == self.COMMAND_SETTING_QUEUE_TYPE_SYNC:
            meta_task = SyncMetaTask(command_key=command_name,
                                     command_config=self.command_config)
        elif queue_type == self.COMMAND_SETTING_QUEUE_TYPE_ASYNC:
            meta_task = AsyncMetaTask(command_key=command_name,
                                      command_config=self.command_config)
        else:
            self.logger.error('Does not support this command: {}, with the queue type: {}'.format(command_name,
                                                                                                  queue_type))
            return None
        return meta_task

    def push_meta_task(self, topic, command_name):
        """
        Push MetaTask into Pulse.
        @param topic: The topic channel.
        @param command_name: the specified command name, which base on cmd_config.json.
        @return:
        """
        # get MetaTask
        meta_task = self.get_meta_task(command_name)
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

        # send
        p.publish(mymessage)

        # disconnect
        p.disconnect()


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
    logging.basicConfig()

    # loading docopt
    arguments = docopt(__doc__)

    # loading config
    config_file = arguments['--config']
    config = CommonUtil.load_json_file(config_file)
    username = config.get('pulse_username')
    password = config.get('pulse_password')

    # loading cmd_config
    cmd_config_file = arguments['--cmd-config']
    command_config = CommonUtil.load_json_file(cmd_config_file)
    if not command_config:
        raise Exception('There is not command config. (Loaded from {})'.format(cmd_config_file))

    # prepare the topic, ex: darwin, win10, win7, linux2
    topic = HasalPulsePublisher.TOPIC_DARWAN
    # prepare command name
    command_name = 'download-latest-nightly'

    # Push MetaTask to Pulse
    publisher = HasalPulsePublisher(username, password, command_config)
    publisher.push_meta_task(topic=topic,
                             command_name=command_name)


if __name__ == '__main__':
    main()
