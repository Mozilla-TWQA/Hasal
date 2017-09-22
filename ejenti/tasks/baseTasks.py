import os
import logging


def init_task(kwargs):
    queue_msg = kwargs.get("queue_msg", {})
    consumer_config = kwargs.get("consumer_config", {})
    task_config = queue_msg.get("cmd_obj", {}).get("configs", {})
    return queue_msg, consumer_config, task_config


def parse_cmd_parameters(input_queue_msg):
    input_cmd_str = input_queue_msg.get("input_cmd_str", "")
    return [spilt_value for spilt_value in input_cmd_str.split(" ") if spilt_value != ""]


def get_hasal_repo_path(task_config):
    current_path_list = os.getcwd().split(os.sep)
    for d_name in reversed(current_path_list):
        if d_name.lower() != "hasal":
            current_path_list.pop()
        else:
            break
    default_repo_path = os.sep.join(current_path_list)
    repo_path = task_config.get("repo_path", default_repo_path)
    return repo_path


def task_checking_sending_queue(sending_queue):
    """
    if the queue is full, then get one item from queue
    """
    if sending_queue.full():
        message_item = sending_queue.get()
        logging.error('The Slack Sending Queue is full, pop one item.\n{line}\n{obj}\n{line}\n'.format(
            line='-' * 10,
            obj=message_item))


def task_generate_slack_sending_message(message, channel='mgt'):
    """
    Wrapper of generate_slack_sending_message() of slack_bot
    """
    if channel not in ['mgt', 'election']:
        channel = 'mgt'
    ret_obj = {
        'message': message,
        'channel': channel
    }
    return ret_obj
