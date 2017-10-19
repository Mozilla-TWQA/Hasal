import os
import copy
import json
import socket
import shutil
import datetime
import logging
from lib.common.b2Util import B2Util
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
    # {"job_name, ex:pulse, slack, interactive": {"utc_timestamp, ex:1508484854": {"status_tag, ex: async_task_consumer":{"status_code":{"utc_timestamp":1508484857,
    #                                                                                                                                    "desc": "hello world",
    #                                                                                                                                    "content": {}
    #                                                                                                                                    }}}}}
    # {"pulse": {"1508484854": {"async_task_consumer": {"100": {"utc_timestamp": "1508484857",
    #                                                           "desc": "get message from local queue",
    #                                                           "content": {}},
    #                                                   "200": {"utc_timestamp": "1508484859",
    #                                                           "desc": "call task",
    #                                                           "content": {}},
    #                                                   "900": {"utc_timestamp": "1508484899",
    #                                                           "desc": "successfully complete",
    #                                                           "content": {}}
    #                                                   },
    #                           "trigger_hasal":{"100":{"utc_timestamp": "1508484999",
    #                                                   "desc": "Start running hasal",
    #                                                   "content": {}}
    #                                            }
    #                           },
    #            "1508499999": {"async_task_consumer": {"100": {"utc_timestamp": "1508484857",
    #                                                           "desc": "get message from local queue",
    #                                                           "content": {}},
    #                                                   "200": {"utc_timestamp": "1508484859",
    #                                                           "desc": "call task",
    #                                                           "content": {}},
    #                                                   "900": {"utc_timestamp": "1508484899",
    #                                                           "desc": "successfully complete",
    #                                                           "content": {}}
    #                                                   },
    #                           "trigger_hasal":{"100":{"utc_timestamp": "1508484999",
    #                                                   "desc": "Start running hasal",
    #                                                   "content": {}}
    #                                            }
    #                           }
    #            },
    #  "slack": {"1518484854": {"async_task_consumer": {"100": {"utc_timestamp": "1508484857",
    #                                                           "desc": "get message from local queue",
    #                                                           "content": {}},
    #                                                   "200": {"utc_timestamp": "1508484859",
    #                                                           "desc": "call task",
    #                                                           "content": {}}
    #                                                   }
    #                           }
    #            }
    #  }

    """
    DEFAULT_DATA_RECENTLY_DEFINE_PERIOD = 7
    DEFAULT_DATA_HISTORY_DEFINE_PERIOD = 30

    # check configs in kwargs
    if "configs" not in kwargs:
        raise Exception("The current input consumer kwargs didn't contain the kwarg [configs]")

    # get config defined parameter [data period define]
    b2_account_id = kwargs['configs'].get("b2_account_id", None)
    b2_account_key = kwargs['configs'].get("b2_account_key", None)
    b2_upload_bucket_name = kwargs['configs'].get("b2_upload_bucket_name", None)
    data_recently_define_period = kwargs['configs'].get("data_recently_define_period", DEFAULT_DATA_RECENTLY_DEFINE_PERIOD)
    data_history_define_period = kwargs['configs'].get("data_recently_define_period", DEFAULT_DATA_HISTORY_DEFINE_PERIOD)

    # get status folder path, status json file name and path
    status_folder_path = StatusFileCreator.get_status_folder()
    current_host_name = socket.gethostname()
    recently_status_json_file_name = "%s_recently.json" % current_host_name
    history_status_json_file_name = "%s_history.json" % current_host_name
    recently_status_json_file_path = os.path.join(status_folder_path, recently_status_json_file_name)
    history_status_json_file_path = os.path.join(status_folder_path, history_status_json_file_name)

    # housekeeping the status folder before generating the status json file
    status_folder_list = [folder_name for folder_name in os.listdir(status_folder_path) if folder_name.startswith(".") is False and CommonUtil.represent_as_int(folder_name.split("-")[1])]
    current_utc_time = datetime.datetime.utcnow()
    outdated_date = current_utc_time - datetime.timedelta(days=data_history_define_period)
    outdated_status_folder_list = [folder_name for folder_name in status_folder_list if datetime.datetime.utcfromtimestamp(int(folder_name.split("-")[1])) < outdated_date]
    for outdated_folder_name in outdated_status_folder_list:
        outdated_folder_path = os.path.join(status_folder_path, outdated_folder_name)
        shutil.rmtree(outdated_folder_path)
        logging.debug("Housekeeping outdated folder [%s]" % outdated_folder_path)

    # generate history period json obj
    # load exisitng history status json file
    if os.path.exists(history_status_json_file_path):
        try:
            with open(history_status_json_file_path) as read_history_status_json_fh:
                history_status_json_obj = json.load(read_history_status_json_fh)
        except Exception, e:
            logging.error("Load history status json file[%s] with error [%s]" % (history_status_json_file_path, e.message))
            history_status_json_obj = {}
    else:
        history_status_json_obj = {}

    # generate status json obj
    history_status_folder_list = [folder_name for folder_name in os.listdir(status_folder_path) if folder_name.startswith(".") is False and CommonUtil.represent_as_int(folder_name.split("-")[1])]
    for history_status_folder_name in history_status_folder_list:
        history_status_folder_path = os.path.join(status_folder_path, history_status_folder_name)
        job_name = history_status_folder_name.split("-")[0]
        job_utc_timestamp_string = history_status_folder_name.split("-")[1]
        task_file_name_list = [task_file_name for task_file_name in os.listdir(history_status_folder_path) if folder_name.startswith(".") is False and CommonUtil.represent_as_int(task_file_name.split("-")[0])]
        for task_file_name in task_file_name_list:
            task_file_path = os.path.join(history_status_folder_path, task_file_name)
            task_name = task_file_name.split("-")[1].split(os.extsep)[0]
            task_status_code = task_file_name.split("-")[0]
            try:
                with open(task_file_path) as read_fh:
                    task_content = json.load(read_fh)
            except Exception, e:
                logging.error("Load task content file[%s] with error [%s]" % e.message)
                task_content = {}
            if job_name in history_status_json_obj:
                if job_utc_timestamp_string in history_status_json_obj[job_name]:
                    if task_name in history_status_json_obj[job_name][job_utc_timestamp_string]:
                        if task_status_code in history_status_json_obj[job_name][job_utc_timestamp_string][task_name]:
                            logging.debug("Skip record task[%s] into history status json file due to status code already exist!" % task_file_path)
                        else:
                            history_status_json_obj[job_name][job_utc_timestamp_string][task_name][task_status_code] = task_content
                    else:
                        history_status_json_obj[job_name][job_utc_timestamp_string][task_name] = {task_status_code: task_content}
                else:
                    history_status_json_obj[job_name][job_utc_timestamp_string] = {task_name: {task_status_code: task_content}}
            else:
                history_status_json_obj[job_name] = {job_utc_timestamp_string: {task_name: {task_status_code: task_content}}}

    # dump history json obj to file
    with open(history_status_json_file_path, "wb") as history_write_fh:
        json.dump(history_status_json_obj, history_write_fh)

    # generate recently period json obj
    recently_status_json_obj = {}
    recently_date = current_utc_time - datetime.timedelta(days=data_recently_define_period)
    for recently_job_name in history_status_json_obj:
        recently_period_timestamp_list = [utc_ts for utc_ts in history_status_json_obj[recently_job_name].keys() if recently_date <= datetime.datetime.utcfromtimestamp(int(utc_ts))]
        recently_status_json_obj[recently_job_name] = {}
        for recently_period_timestamp in recently_period_timestamp_list:
            recently_status_json_obj[recently_job_name][recently_period_timestamp] = copy.deepcopy(history_status_json_obj[recently_job_name][recently_period_timestamp])

    # dump recently json obj to file
    with open(recently_status_json_file_path, "wb") as recently_write_fh:
        json.dump(recently_status_json_obj, recently_write_fh)

    # upload to b2
    b2_obj = B2Util(b2_account_id, b2_account_key)
    history_status_json_url = b2_obj.upload_file(history_status_json_file_path, b2_upload_bucket_name)
    recently_status_json_url = b2_obj.upload_file(recently_status_json_file_path, b2_upload_bucket_name)

    if not history_status_json_url:
        logging.error("Upload history status json file failed!")

    if not recently_status_json_url:
        logging.error("Upload recently status json file failed!")

    if history_status_json_url and recently_status_json_url:
        logging.debug("Upload history and recently status json file success!!")
