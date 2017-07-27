import os


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
