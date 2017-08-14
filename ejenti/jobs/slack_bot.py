import os
import json
import time
import random
import socket
import logging

from datetime import datetime
from slackclient import SlackClient


DEFAULT_VERIFY_KWARGS_LIST = ['sync_queue', 'async_queue', 'configs']

DEFAULT_DELAY_SEC = 1

KEY_CMD_CONFIG = 'cmd_config'

KEY_BOT_NAME = 'bot_name'
KEY_BOT_API_TOKEN = 'bot_api_token'
KEY_BOT_MGT_CHANNEL = 'bot_mgt_channel'
KEY_BOT_ELECTION_CHANNEL = 'bot_election_channel'

ELECTION_SHORT_TIMEOUT = 60
ELECTION_TIMEOUT = 10 * 60
ELECTION_TIMEOUT_RANDOM_OFFSET = 60
ELECTION_LEADER_HEARTBEAT = 5 * 60
ELECTION_SEND_MSG_DELAY = 5

ELECTION_BOT_FOLLOWER = 'FOLLOWER'
ELECTION_BOT_CANDIDATE = 'CANDIDATE'
ELECTION_BOT_LEADER = 'LEADER'

ELECTION_MSG_HEARTBEAT = 'HB'
ELECTION_MSG_ELECTION = 'ELEC'


def verify_consumer_kwargs(kwargs):
    for verify_kwargs_key in DEFAULT_VERIFY_KWARGS_LIST:
        if verify_kwargs_key not in kwargs:
            raise Exception("The current input consumer kwargs didn't contain the kwarg [%s]" % verify_kwargs_key)


def init_consumer(kwargs):
    # verify kwargs
    verify_consumer_kwargs(kwargs)


def init_slack_bot(**kwargs):
    """
    Init Slack Bot
    @param kwargs:
    @return:
    """
    init_consumer(kwargs)

    # prepare username, password, and label
    configs = kwargs.get('configs')
    bot_name = configs.get(KEY_BOT_NAME)
    bot_api_token = configs.get(KEY_BOT_API_TOKEN)
    bot_mgt_channel_name = configs.get(KEY_BOT_MGT_CHANNEL)
    bot_election_channel_name = configs.get(KEY_BOT_ELECTION_CHANNEL)

    # verify Slack configs
    if not bot_name or not bot_api_token \
            or not bot_mgt_channel_name or not bot_election_channel_name:
        # there is no Pulse account information in "job_config.json"
        logging.error('Cannot access Slack due to there is no Slack BOT API information,'
                      ' please check {} file.'.format('job_config'))
        return

    # get cmd_config
    cmd_config = kwargs.get(KEY_CMD_CONFIG)

    # init the slack_client
    slack_client = SlackClient(bot_api_token)

    try:
        # https://api.slack.com/methods/rtm.connect
        if slack_client.rtm_connect():
            # find Bot ID
            bot_user_obj = get_bot_user_obj(slack_client, bot_name)
            bot_id = bot_user_obj.id
            logging.debug('\nName: {botname}\nID: {botid}\nIP: {ip}\nPID: {pid}'.format(botname=bot_name,
                                                                                        botid=bot_id,
                                                                                        ip=get_current_ip(),
                                                                                        pid=os.getpid()))

            bot_mgt_channel_obj = find_channel(slack_client, bot_mgt_channel_name)
            bot_mgt_channel_id = bot_mgt_channel_obj.id

            # for Bots Election
            bot_election_channel_obj = find_channel(slack_client, bot_election_channel_name)
            bot_election_channel_id = bot_election_channel_obj.id
            election_leader_heartbeat = ELECTION_LEADER_HEARTBEAT
            election_timeout = ELECTION_SHORT_TIMEOUT
            election_type = ELECTION_BOT_FOLLOWER

            while True:
                rtm_ret_list = slack_client.rtm_read()
                if rtm_ret_list:
                    for rtm_ret in rtm_ret_list:
                        channel_id = rtm_ret.get('channel')

                        if channel_id == bot_election_channel_id:
                            # handle Bots election
                            election_leader_heartbeat, election_timeout, election_type = handle_election(slack_client,
                                                                                                         rtm_ret,
                                                                                                         election_leader_heartbeat,
                                                                                                         election_timeout,
                                                                                                         election_type,
                                                                                                         bot_user_obj,
                                                                                                         bot_election_channel_obj)

                        elif channel_id == bot_mgt_channel_id:
                            # handle RTM response
                            handle_rtm(slack_client, rtm_ret, configs, cmd_config, election_type, bot_user_obj, bot_mgt_channel_obj)

                # election counter
                election_leader_heartbeat, election_timeout, election_type = handle_election_counter(slack_client,
                                                                                                     election_leader_heartbeat,
                                                                                                     election_timeout,
                                                                                                     election_type,
                                                                                                     bot_election_channel_obj)

                time.sleep(DEFAULT_DELAY_SEC)

    except Exception as e:
        logging.error(e)


def handle_election(slack_client, rtm_ret, election_leader_heartbeat, election_timeout, election_type, bot_user_obj,
                    bot_election_channel_obj):
    """
    Handle Bot Election.
    @param slack_client:
    @param rtm_ret:
    @param election_leader_heartbeat: Leader heartbeat counter
    @param election_timeout: Election timeout counter
    @param election_type: Election Type. 'FOLLOWER', 'CANDIDATE', or 'LEADER'
    @param bot_user_obj:
    @param bot_election_channel_obj:
    @return: election_leader_heartbeat, election_timeout, election_type
    """
    user_id = rtm_ret.get('user')
    # if the election message comes from other user, then skip it.
    if user_id != bot_user_obj.id:
        return election_leader_heartbeat, election_timeout, election_type

    text = rtm_ret.get('text')
    if text:
        message = text.encode('utf-8')
    else:
        return election_leader_heartbeat, election_timeout, election_type

    try:
        dict_obj = json.loads(message)

        logging.debug('Handle Election Channel: {}'.format(dict_obj))

        input_type = dict_obj.get('type')
        input_power = dict_obj.get('power')
        current_power = get_bot_power_for_election()

        if input_type == ELECTION_MSG_ELECTION:
            # all Bot will go into election mode
            logging.debug('Do Election ...')
            if current_power > input_power:
                logging.debug('Power more than other, do election! IP {ip}, PID {pid}'.format(ip=get_current_ip(),
                                                                                              pid=os.getpid()))
                if election_type == ELECTION_BOT_CANDIDATE:
                    # already be candidate, does not need to reset timeout
                    pass
                else:
                    election_type = ELECTION_BOT_CANDIDATE
                    election_leader_heartbeat = ELECTION_LEADER_HEARTBEAT
                    election_timeout = ELECTION_SHORT_TIMEOUT

                # wait 1~3 sec
                time.sleep(random.randint(0, ELECTION_SEND_MSG_DELAY))
                send_election(slack_client, ELECTION_MSG_ELECTION, bot_election_channel_obj)

            elif current_power < input_power:
                logging.debug('Power less than other, I am follower! IP {ip}, PID {pid}'.format(ip=get_current_ip(),
                                                                                                pid=os.getpid()))
                election_type = ELECTION_BOT_FOLLOWER
                election_leader_heartbeat = ELECTION_LEADER_HEARTBEAT
                election_timeout = ELECTION_TIMEOUT + random.randint(0, ELECTION_TIMEOUT_RANDOM_OFFSET)
            else:
                # if get the same power, skip
                pass

        elif input_type == ELECTION_MSG_HEARTBEAT:
            # if I am leader, and get heartbeat message comes from other bot, then election
            if election_type == ELECTION_BOT_LEADER and current_power != input_power:
                logging.debug('I found other leader, do election! IP {ip}, PID {pid}'.format(ip=get_current_ip(),
                                                                                             pid=os.getpid()))
                election_type = ELECTION_BOT_CANDIDATE
                election_leader_heartbeat = ELECTION_LEADER_HEARTBEAT
                election_timeout = ELECTION_SHORT_TIMEOUT
                # wait 1~3 sec
                time.sleep(random.randint(0, ELECTION_SEND_MSG_DELAY))
                send_election(slack_client, ELECTION_MSG_ELECTION, bot_election_channel_obj)

            elif election_type == ELECTION_BOT_LEADER and current_power == input_power:
                # if get the same power, skip
                pass

            else:
                # reset timeout counter
                election_leader_heartbeat = ELECTION_LEADER_HEARTBEAT
                election_timeout = ELECTION_TIMEOUT + random.randint(0, ELECTION_TIMEOUT_RANDOM_OFFSET)

    except Exception as e:
        logging.error(e)

    return election_leader_heartbeat, election_timeout, election_type


def handle_election_counter(slack_client, election_leader_heartbeat, election_timeout, election_type,
                            bot_election_channel_obj):
    """
    Handle the Bot Election counter.
    @param slack_client:
    @param election_leader_heartbeat: Leader heartbeat counter
    @param election_timeout: Election timeout counter
    @param election_type: Election Type. 'FOLLOWER', 'CANDIDATE', or 'LEADER'
    @param bot_election_channel_obj:
    @return: election_leader_heartbeat, election_timeout, election_type
    """
    if election_type == ELECTION_BOT_LEADER:
        # Leader will send HeartBeat to other when election_leader_heartbeat less than 0
        election_leader_heartbeat -= 1
        if election_leader_heartbeat <= 0:
            # send heartbeat
            election_leader_heartbeat = ELECTION_LEADER_HEARTBEAT
            send_election(slack_client, ELECTION_MSG_HEARTBEAT, bot_election_channel_obj)

    elif election_type == ELECTION_BOT_FOLLOWER:
        # Follower will wait HeartBeat or Election, send election when election_timeout less than 0.
        election_timeout -= 1
        if election_timeout <= 0:
            election_type = ELECTION_BOT_CANDIDATE
            election_timeout = ELECTION_SHORT_TIMEOUT
            # send election
            send_election(slack_client, ELECTION_MSG_ELECTION, bot_election_channel_obj)

    elif election_type == ELECTION_BOT_CANDIDATE:
        # Candidate will wait election_timeout to 0, become Leader if there is no other candidates.
        election_timeout -= 1
        if election_timeout <= 0:
            logging.debug('Wow... I am Leader! I will tell other bots.')
            election_type = ELECTION_BOT_LEADER
            election_timeout = ELECTION_TIMEOUT
            election_leader_heartbeat = ELECTION_LEADER_HEARTBEAT
            # send heartbeat
            send_election(slack_client, ELECTION_MSG_HEARTBEAT, bot_election_channel_obj)

    return election_leader_heartbeat, election_timeout, election_type


def send_election(slack_client, message_type, bot_election_channel_obj):
    """
    Send Election message or HeartBeat message.
    @param slack_client:
    @param message_type: string. 'HB' or 'ELEC'.
    @param bot_election_channel_obj:
    """
    now = datetime.now()
    now_string = now.strftime('%Y-%m-%d_%H:%M:%S.%f')
    message = {
        'type': message_type,
        'ip': get_current_ip(),
        'pid': os.getpid(),
        'power': get_bot_power_for_election(),
        'time': now_string
    }
    send(slack_client, message, bot_election_channel_obj)


def ip_2_int(ip_string):
    """
    Input IP address string, and then return int.
    Ex: '192.168.0.1' => 3232235521
    @param ip_string:
    @return: IP integer number.
    """
    return reduce(lambda out, x: (out << 8) + int(x), ip_string.split('.'), 0)


def get_current_ip():
    """
    return current IP address.
    """
    return socket.gethostbyname(socket.gethostname())


def get_bot_power_for_election():
    """
    Get the current Bot election power base on IP and PID.
    @return: A integer number <IP to Int><PID>. for example, 323223552119772.
    """
    ip = get_current_ip()
    pid = os.getpid()
    return int('{}{}'.format(ip_2_int(ip), pid))


def handle_rtm(slack_client, rtm_ret, configs, cmd_config, election_type, bot_user_obj, bot_mgt_channel_obj):
    """
    Handle Slack RTM message.
    Ref: https://api.slack.com/rtm
    @param slack_client:
    @param rtm_ret:
    @param configs: job configs
    @param cmd_config: cmd_config settings dict object
    @param election_type: current election type, leader will do more than others
    @param bot_user_obj:
    @param bot_mgt_channel_obj:
    @return:
    """
    EVENT_TYPES_HANDLERS = {
        'message': handle_rtm_message
    }

    evt_type = rtm_ret.get('type')
    for evt in EVENT_TYPES_HANDLERS.keys():
        if evt == evt_type:
            return EVENT_TYPES_HANDLERS[evt](slack_client, rtm_ret, configs, cmd_config, election_type, bot_user_obj, bot_mgt_channel_obj)
    return False


def handle_rtm_message(slack_client, rtm_ret, configs, cmd_config, election_type, bot_user_obj, bot_mgt_channel_obj):
    """
    Handle Slack RTM message which type is "message".
    @param slack_client:
    @param rtm_ret:
    @param configs: job configs
    @param cmd_config: cmd_config settings dict object
    @param election_type: current election type, leader will do more than others
    @param bot_user_obj:
    @param bot_mgt_channel_obj:
    @return:
    """
    bot_id = bot_user_obj.id

    # if message changed, it will have subtype
    if rtm_ret.get('subtype') == 'message_changed':
        new_msg = rtm_ret.get('message')
        if new_msg:
            text = new_msg.get('text')
            # getting user id
            user_id = new_msg.get('user')
        else:
            return False
    else:
        # getting message text
        text = rtm_ret.get('text')
        # getting user id
        user_id = rtm_ret.get('user')

    if text:
        message = text.encode('utf-8')
    else:
        return False

    # Skip if message comes from bot it-self
    if user_id == bot_id:
        logging.debug('Message from Bot: {msg}, skip.'.format(msg=message))
        return False

    # getting channel and user name
    user_obj = find_user(slack_client, user_id)
    user_name = user_obj.name if user_obj else ''
    logging.debug('=> handle_rtm_message\n'
                  'User/ID: {u} / {uid}\nText: {t}'.format(u=user_name,
                                                           uid=user_id,
                                                           t=message))


def send(slack_client, message, channel_obj):
    """
    Send slack message.
    @param slack_client:
    @param message:
    @param channel_obj:
    @return:
    """
    ret = slack_client.api_call("chat.postMessage", channel=channel_obj.id, text=message, as_user=True)
    if not ret.get('ok'):
        logging.error('Sending message failed!\n{ret}'.format(ret=ret))
        return False
    return True


def get_bot_user_obj(slack_client, bot_name):
    """
    The method find_user() will return a User object.
        id : U6LNC9BN0
        tz : None
        name : hasal-bot
        real_name : Hasal Bot
    @param slack_client:
    @param bot_name:
    @return: Bot User info.
    """
    return find_user(slack_client, bot_name)


def find_user(slack_client, search_string):
    """
    User object has following attributes:
        - name
        - tz
        - real_name
        - server
        - id
    Ref:
        https://github.com/slackapi/python-slackclient/blob/master/slackclient/_user.py
        https://github.com/slackapi/python-slackclient/blob/master/slackclient/_util.py
            SearchDict
    :param slack_client:
    :param search_string:
    :return:
    """
    return slack_client.server.users.find(search_string)


def find_channel(slack_client, search_string):
    """
    Channel object has following attributes:
        - name
        - id
        - members
        - server
    Ref:
        https://github.com/slackapi/python-slackclient/blob/master/slackclient/_channel.py
        https://github.com/slackapi/python-slackclient/blob/master/slackclient/_util.py
            SearchList
    :param slack_client:
    :param search_string:
    :return:
    """
    return slack_client.server.channels.find(search_string)
