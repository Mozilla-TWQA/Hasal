import os
import copy
import json
import logging
from lib.common.commonUtil import CommonUtil
from lib.thirdparty.tee import system2
from baseTasks import init_task
from baseTasks import get_hasal_repo_path
from baseTasks import parse_cmd_parameters
from firefoxBuildTasks import download_latest_nightly_build
from firefoxBuildTasks import deploy_fx_package


def merge_user_input_config_with_default_config(user_input_config, default_config):
    return_config = copy.deepcopy(default_config)
    for config_parent_name in return_config:
        config_parent_obj = user_input_config.get(config_parent_name, {})
        if config_parent_obj:
            for config_name in config_parent_obj:
                if config_name in return_config[config_parent_name]:
                    return_config[config_parent_name][config_name] = config_parent_obj[config_name]
                else:
                    logging.error("User input config [%s] is not match with default config [%s]" % (user_input_config, default_config))
        else:
            logging.error("User input config [%s] is not match with default config [%s]" % (user_input_config, default_config))
    return return_config


def generate_config_path_json_mapping(input_path, input_json_obj, output_result):
    for path in input_json_obj:
        n_path = os.path.join(input_path, path)
        if n_path.endswith(".json"):
            output_result[n_path] = input_json_obj[path]
        else:
            generate_config_path_json_mapping(n_path, input_json_obj[path], output_result)
    return output_result


def run_hasal_on_latest_nightly(**kwargs):
    # download latest nightly build
    pkg_download_info_json = download_latest_nightly_build(**kwargs)

    # deploy fx
    # specify firefox downloaded package path
    kwargs['queue_msg']['cmd_obj']['configs']['fx_dl_pkg_path'] = pkg_download_info_json['FX-DL-PACKAGE-PATH']
    if deploy_fx_package(**kwargs):

        # generate hasal
        meta_task_input_config = kwargs['queue_msg']['cmd_obj']['configs'].get("input_config", {})
        auto_generate_config = {"configs": {"upload": {
            "default.json": {"perfherder-revision": pkg_download_info_json['PERFHERDER-REVISION'],
                             "perfherder-pkg-platform": pkg_download_info_json['PERFHERDER-PKG-PLATFORM']}}}}
        merge_input_config = CommonUtil.deep_merge_dict(meta_task_input_config, auto_generate_config)
        kwargs['queue_msg']['cmd_obj']['configs']['input_config'] = merge_input_config
        ejenti_hasal_config = generate_hasal_config(**kwargs)

        # exec hasal runtest
        kwargs['queue_msg']['cmd_obj']['configs']['specify_config_settings'] = ejenti_hasal_config
        exec_hasal_runtest(**kwargs)


def generate_hasal_config(**kwargs):
    """
    generate hasal config jsons for ejenti, default should generate agent/chrome/exec/firefox/global/index/online jsons
    input_config example:
    user
    => exec=default, index=il
    slack agent
    =>
    {
        "configs": {
            "exec": {
                "default.json": {
                    "key1": "value1"
                }
            },
            "firefox": {
                "default.json": {
                    "key2": "value2",
                    "key3": "value3"
                    }
            },
            "online": {
                "abc.json":{
                    "key3": "value3",
                    "key4": "value4"
                    }
            }
        }
    }
    @param kwargs: will have two keys queue_msg, consumer_config
    @return:
    """

    DEFAULT_HASAL_CONFIG = {
        "configs": {
            "exec": {"default.json": {}},
            "firefox": {"default.json": {}},
            "chrome": {"default.json": {}},
            "index": {"runtimeDctGenerator.json": {}},
            "upload": {"default.json": {}},
            "global": {"default.json": {}}
        }
    }

    DEFAULT_HASAL_RUNTEST_CONFIGS = {
        "--exec-config": "",
        "--firefox-config": "",
        "--index-config": "",
        "--upload-config": "",
        "--global-config": "",
        "--chrome-config": ""
    }

    # get queue msg, consumer config from kwargs
    queue_msg, consumer_config, task_config = init_task(kwargs)

    # get override config
    cmd_parameter_list = queue_msg.get('input_cmd_str', "").split(" ", 1)

    default_config_settings = task_config.get("default_config_settings", DEFAULT_HASAL_CONFIG)
    default_runtest_configs = task_config.get("default_runtest_configs", DEFAULT_HASAL_RUNTEST_CONFIGS)

    # get input config from user interactive mode
    if len(cmd_parameter_list) == 2:
        input_json_str = cmd_parameter_list[1]
        logging.debug("input cmd parameter : [%s]" % input_json_str)
        input_json_obj = CommonUtil.load_json_string(input_json_str)
        logging.debug("load json obj from input cmd: [%s]" % input_json_obj)
    else:
        input_json_obj = task_config.get("input_config", {})
        logging.debug("load json obj from input config: [%s]" % input_json_obj)

    if len(input_json_obj.keys()) == 0:
        logging.info("No input config object [%s] detected, will use the default config setting instead" % input_json_obj)
    else:
        json_path = get_hasal_repo_path(task_config)

        # merge default and input
        full_config_obj = merge_user_input_config_with_default_config(input_json_obj, default_config_settings)

        # generate config path and need to modify key-value pair dict
        full_config_path_mapping = generate_config_path_json_mapping(json_path, full_config_obj, {})

        full_exec_runtest_config = copy.deepcopy(default_runtest_configs)

        # dump to json file
        for config_path in full_config_path_mapping:
            tmp_json_obj = CommonUtil.load_json_file(config_path)
            tmp_json_obj.update(full_config_path_mapping[config_path])
            dir_name = os.path.dirname(config_path)
            new_config_path = os.path.join(dir_name, "ejenti.json")
            parameter_name = "--{}-config".format(dir_name.split(os.sep)[-1])
            full_exec_runtest_config[parameter_name] = new_config_path
            with open(new_config_path, 'w') as fh:
                json.dump(tmp_json_obj, fh)
        logging.debug("exec runtest config [%s]" % full_exec_runtest_config)
        return full_exec_runtest_config


def exec_hasal_runtest(**kwargs):
    """
    a wrapper to wrap the runtest cmd
    @param kwargs:
    @return:
    """
    DEFAULT_RUNTEST_CMD_FMT = ["python", "runtest.py"]
    DEFAULT_JOB_LOG_FN = "hasal_runtest.log"

    # get queue msg, consumer config from kwargs
    queue_msg, consumer_config, task_config = init_task(kwargs)

    # get input cmd parameters
    cmd_parameter_list = parse_cmd_parameters(queue_msg)

    # get setting from task config
    default_cmd_fmt = task_config.get("default_cmd_fmt", DEFAULT_RUNTEST_CMD_FMT)
    default_log_fn = task_config.get("default_log_fn", DEFAULT_JOB_LOG_FN)
    specify_config_settings = task_config.get("specify_config_settings", {})
    workding_dir = get_hasal_repo_path(task_config)
    exec_cmd_list = copy.deepcopy(default_cmd_fmt)

    if len(cmd_parameter_list) > 1:
        exec_cmd_list.extend(cmd_parameter_list[1:])
    else:
        for config_name in specify_config_settings:
            exec_cmd_list.extend([config_name, specify_config_settings[config_name]])

    exec_cmd_str = " ".join(exec_cmd_list)
    system2(exec_cmd_str, cwd=workding_dir, logger=default_log_fn, stdout=True, exec_env=os.environ.copy())
