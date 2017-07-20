def init_task(kwargs):
    queue_msg = kwargs.get("queue_msg", {})
    consumer_config = kwargs.get("consumer_config", {})
    task_config = queue_msg.get("cmd_obj", {}).get("configs", {})
    return queue_msg, consumer_config, task_config


def parse_cmd_parameters(input_queue_msg):
    input_cmd_str = input_queue_msg.get("input_cmd_str", "")
    return [spilt_value for spilt_value in input_cmd_str.split(" ") if spilt_value != ""]
