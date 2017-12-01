import os
import copy
import json
import socket
import shutil
import datetime
import logging
from lib.common.gistUtil import GISTUtil
from lib.common.commonUtil import CommonUtil
from lib.common.statusFileCreator import StatusFileCreator


def status_json_creator(**kwargs):
    """
    Job Function for status json creator
    @param kwargs:
    @return:
     data example:
    # status json format
    # host_name.json
    # {
    "data":[
        {
            "type": "interactive",
            "start_ts": "1234567890",
            "cmd": "interactive",
            "status": [
                {
                    "code": "100",
                    "status_code_desc": "Get command from interactive mode",
                    "utc_timestamp": "1234567898"
                    "fn_code": "100"
                },
                {
                    "code": "200",
                    "status_code_desc": "Get command from interactive mode",
                    "utc_timestamp": "1234567899"
                    "fn_code": "200"
                },
                {
                    "code": "900",
                    "status_code_desc": "Get command from interactive mode",
                    "utc_timestamp": "1234567900"
                    "fn_code": "900"
                }
            ]
        },
        {
            "type": "interactive",
            "start_ts": "2345678901",
            "cmd": "interactive",
            "status": [
                {
                    "code": "100",
                    "status_code_desc": "Get command from interactive mode",
                    "utc_timestamp": "1234567898"
                    "fn_code": "100"
                },
                {
                    "code": "300",
                    "status_code_desc": "Get command from interactive mode",
                    "utc_timestamp": "1234567899",
                    "fn_code": "300-1"
                }
            ]
        },
        {
            "type": "interactive",
            "start_ts": "3456789012",
            "cmd": "interactive",
            "status": [
                {
                    "code": "100",
                    "status_code_desc": "Get command from interactive mode",
                    "utc_timestamp": "1234567898"
                    "fn_code": "100-1",
                }
            ]
        }
    ]
}
    #                           }
    #            }
    #  }

    """
    DEFAULT_DATA_RECENTLY_DEFINE_PERIOD = 3
    DEFAULT_DATA_HISTORY_DEFINE_PERIOD = 3

    # check configs in kwargs
    if "configs" not in kwargs:
        raise Exception("The current input consumer kwargs didn't contain the kwarg [configs]")

    # get config defined parameter [data period define]
    gist_user_name = kwargs['configs'].get("gist_user_name", None)
    gist_auth_token = kwargs['configs'].get("gist_auth_token", None)
    data_recently_define_period = kwargs['configs'].get("data_recently_define_period", DEFAULT_DATA_RECENTLY_DEFINE_PERIOD)
    data_history_define_period = kwargs['configs'].get("data_recently_define_period", DEFAULT_DATA_HISTORY_DEFINE_PERIOD)

    # get status folder path, status json file name and path
    status_folder_path = StatusFileCreator.get_status_folder()
    current_host_name = socket.gethostname()
    recently_status_json_file_name = "%s_recently.json" % current_host_name
    history_status_json_file_name = "%s_history.json" % current_host_name
    info_status_json_file_name = "%s_info.json" % current_host_name
    recently_status_json_file_path = os.path.join(status_folder_path, recently_status_json_file_name)
    history_status_json_file_path = os.path.join(status_folder_path, history_status_json_file_name)
    info_status_json_file_path = os.path.join(status_folder_path, info_status_json_file_name)

    # housekeeping the status folder before generating the status json file
    status_folder_list = [folder_name for folder_name in os.listdir(status_folder_path) if
                          folder_name.startswith(".") is False and
                          len(folder_name.split("-")) >= 2 and
                          CommonUtil.represent_as_int(folder_name.split("-")[1])]
    current_utc_time = datetime.datetime.utcnow()
    outdated_date = current_utc_time - datetime.timedelta(days=data_history_define_period)
    outdated_status_folder_list = [folder_name for folder_name in status_folder_list if datetime.datetime.utcfromtimestamp(int(folder_name.split("-")[1])) < outdated_date]
    for outdated_folder_name in outdated_status_folder_list:
        outdated_folder_path = os.path.join(status_folder_path, outdated_folder_name)
        shutil.rmtree(outdated_folder_path)
        logging.debug("Housekeeping outdated folder [%s]" % outdated_folder_path)

    # generate history period json obj
    history_status_json_obj = {"data": []}
    history_reference_data_table = {}

    # load exisitng history status json file
    if os.path.exists(history_status_json_file_path):
        try:
            with open(history_status_json_file_path) as read_history_status_json_fh:
                history_reference_obj = json.load(read_history_status_json_fh)

                # convert existing data to reference table
                if len(history_reference_obj["data"]) > 0:
                    for data_obj in history_reference_obj["data"]:
                        job_name = data_obj["type"]
                        job_utc_ts = data_obj["start_ts"]
                        task_name = data_obj["cmd"]
                        for status_obj in data_obj["status"]:
                            status_code = status_obj["fn_code"]
                            if job_name in history_reference_data_table:
                                if job_utc_ts in history_reference_data_table[job_name]:
                                    if task_name in history_reference_data_table[job_name][job_utc_ts]:
                                        if status_code in history_reference_data_table[job_name][job_utc_ts][task_name]:
                                            logging.error("Skip inject job obj into reference due to status code duplicated!!!, job_name:[%s], job_utc_ts:[%s], task_name:[%s], status_code:[%s]" % (job_name, job_utc_ts, task_name, status_code))
                                        else:
                                            history_reference_data_table[job_name][job_utc_ts][task_name][
                                                status_code] = status_obj
                                    else:
                                        history_reference_data_table[job_name][job_utc_ts][task_name] = {
                                            status_code: status_obj}
                                else:
                                    history_reference_data_table[job_name][job_utc_ts] = {
                                        task_name: {status_code: status_obj}}
                            else:
                                history_reference_data_table[job_name] = {
                                    job_utc_ts: {task_name: {status_code: status_obj}}}
        except Exception, e:
            logging.error(
                "Load history status json file[%s] with error [%s]" % (history_status_json_file_path, e.message))

    # generate history status json obj
    # generate folder list, the folder name must comply the naming rule (statusTag_timestamp), and the statusTag cannot
    # in the STATUS_CONCAT_TAG_LIST
    history_status_folder_list = [folder_name for folder_name in os.listdir(status_folder_path) if
                                  folder_name.startswith(".") is False and
                                  len(folder_name.split("-")) >= 2 and
                                  CommonUtil.represent_as_int(folder_name.split("-")[1]) and
                                  folder_name.split("-")[0] not in StatusFileCreator.STATUS_CONCAT_TAG_LIST]

    for history_status_folder_name in history_status_folder_list:
        history_status_folder_path = os.path.join(status_folder_path, history_status_folder_name)
        job_name = history_status_folder_name.split("-")[0]
        job_utc_timestamp_string = history_status_folder_name.split("-")[1]
        task_file_name_list = [task_file_name for task_file_name in os.listdir(history_status_folder_path) if task_file_name.startswith(".") is False and CommonUtil.represent_as_int(task_file_name.split("-")[0])]
        task_with_extname_list = list(set([task_file_name.split("-")[-1] for task_file_name in task_file_name_list]))
        for task_with_extname in task_with_extname_list:
            task_name = task_with_extname.split(os.extsep)[0]
            data_obj = {"type": job_name,
                        "start_ts": job_utc_timestamp_string,
                        "cmd": task_name,
                        "status": []}
            task_code_file_list = [task_file_name for task_file_name in task_file_name_list if task_file_name.split("-")[-1].split(os.extsep)[0] == task_name]
            for task_code_file_name in task_code_file_list:
                # fn_code means the real status code in file name ex: 900-1-pulse.json, fn_code would be 900-1 and code would be 900
                # if example: 900-pulse.json, fn_code would be 900, code would be 900
                fn_task_code = "-".join(task_code_file_name.split("-")[:-1])
                task_code = task_code_file_name.split("-")[0]
                history_reference_data = history_reference_data_table.get(job_name, {}).get(job_utc_timestamp_string, {}).get(task_name, {}).get(fn_task_code, None)
                if history_reference_data:
                    data_obj["status"].append(history_reference_data)
                else:
                    task_code_file_path = os.path.join(history_status_folder_path, task_code_file_name)
                    task_code_obj = CommonUtil.load_json_file(task_code_file_path)
                    task_code_obj["code"] = task_code
                    task_code_obj["fn_code"] = fn_task_code
                    data_obj["status"].append(task_code_obj)
            history_status_json_obj["data"].append(data_obj)

    # dump history json obj to file
    with open(history_status_json_file_path, "wb") as history_write_fh:
        json.dump(history_status_json_obj, history_write_fh)

    # generate recently period json obj
    recently_status_json_obj = {"data": []}
    recently_date = current_utc_time - datetime.timedelta(days=data_recently_define_period)
    for recently_job_obj in history_status_json_obj["data"]:
        if recently_date <= datetime.datetime.utcfromtimestamp(int(recently_job_obj["start_ts"])):
            recently_status_json_obj["data"].append(copy.deepcopy(recently_job_obj))

    # dump recently json obj to file
    with open(recently_status_json_file_path, "wb") as recently_write_fh:
        json.dump(recently_status_json_obj, recently_write_fh)

    # generate info status json obj
    info_status_json_obj = {}
    info_status_folder_list = [folder_name for folder_name in os.listdir(status_folder_path) if
                               folder_name.startswith(".") is False and
                               len(folder_name.split("-")) >= 2 and
                               CommonUtil.represent_as_int(folder_name.split("-")[1]) and
                               folder_name.split("-")[0] in StatusFileCreator.STATUS_CONCAT_TAG_LIST]

    # only keep the distinguish tag
    info_status_reduced_tag_list = set([f_name.split("-")[0] for f_name in info_status_folder_list])

    # filter the tag folder with latest timestamp
    info_status_reduced_list = [sorted_list[0] for sorted_list in [
        sorted([d_name for d_name in info_status_folder_list if tag_name == d_name.split("-")[0]],
               key=lambda x: int(x.split("-")[1]), reverse=True) for tag_name in info_status_reduced_tag_list]]

    # info status will only record the statuscontent of the status 900 into result
    for info_status_folder_name in info_status_reduced_list:
        info_status_folder_path = os.path.join(status_folder_path, info_status_folder_name)
        info_job_name = info_status_folder_name.split("-")[0]
        info_job_utc_timestamp_string = info_status_folder_name.split("-")[1]
        info_task_file_name_list = [task_file_name for task_file_name in os.listdir(info_status_folder_path) if task_file_name.startswith(".") is False and CommonUtil.represent_as_int(task_file_name.split("-")[0])]
        info_status_json_obj[info_job_name] = {"job_utc_timestamp": info_job_utc_timestamp_string}
        for info_task_file_name in info_task_file_name_list:
            info_task_status_code = info_task_file_name.split(os.extsep)[0].split("-")[0]
            if int(info_task_status_code) == 900:
                info_task_file_path = os.path.join(info_status_folder_path, info_task_file_name)
                info_task_name = info_task_file_name.split(os.extsep)[0].split("-")[1]
                info_status_json_obj[info_job_name][info_task_name] = CommonUtil.load_json_file(info_task_file_path)

    # dump info json obj to file
    with open(info_status_json_file_path, "wb") as info_write_fh:
        json.dump(info_status_json_obj, info_write_fh)

    # upload to gist
    gist_obj = GISTUtil(gist_user_name, gist_auth_token)
    info_status_json_url = gist_obj.upload_file(info_status_json_file_path)
    history_status_json_url = gist_obj.upload_file(history_status_json_file_path)
    recently_status_json_url = gist_obj.upload_file(recently_status_json_file_path)

    if not info_status_json_url:
        logging.error("Upload info status json file failed!")

    if not history_status_json_url:
        logging.error("Upload history status json file failed!")

    if not recently_status_json_url:
        logging.error("Upload recently status json file failed!")

    if info_status_json_url and history_status_json_url and recently_status_json_url:
        logging.debug("Upload info, history and recently status json file success!!")
