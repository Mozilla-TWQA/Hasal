import os
import copy
import json
from commonUtil import CommonUtil
from logConfig import get_logger
logger = get_logger(__name__)


class StatusFileCreator(object):
    DEFAULT_STATUS_FOLDER_NAME = "status"

    STATUS_TAG_PULSE = "pulse"
    STATUS_TAG_PULSE_TRIGGER = "pulse_trigger"
    STATUS_TAG_PULSE_TRIGGER_BACKFILL = "pulse_trigger_backfill"
    STATUS_TAG_SLACK = "slack"
    STATUS_TAG_INTERACTIVE = "interactive"
    STATUS_TAG_SYNC_TASK_CONSUMER = "sync_task_consumer"
    STATUS_TAG_ASYNC_TASK_CONSUMER = "async_task_consumer"

    # githubTasks.py
    STATUS_TAG_GIT_RESET = "git_reset"
    STATUS_TAG_GIT_FETCH = "git_fetch"
    STATUS_TAG_GIT_CHECKOUT = "git_checkout"
    STATUS_TAG_GIT_PULL = "git_pull"

    # firefoxBuildTasks.py
    STATUS_TAG_DOWNLOAD_NIGHTLY = "download_nightly"
    STATUS_TAG_DEPLOY_FIREFOX_PKG = "deploy_firefox_pkg"

    # hasalTasks.py
    STATUS_TAG_GENERATE_HASAL_CONFIG = "generate_hasal_config"
    STATUS_TAG_RUN_HASAL_RUNTEST_CMD = "run_hasal_runtest_cmd"

    # runtest.py
    STATUS_TAG_RUNTEST_CMD = "runtest_cmd"

    # common tempate
    STATUS_CODE_DESC_CMD_EXECUTED_SUCCESSFULLY = "Successfully complete"

    STATUS_CODE_GENERAL_CMD_TEMPLATE = {100: "Prepare to execute the command",
                                        800: "Failed on exeucting the command",
                                        900: STATUS_CODE_DESC_CMD_EXECUTED_SUCCESSFULLY}

    STATUS_CODE_MAPPING = {STATUS_TAG_PULSE: {100: "Get message from pulse queue",
                                              200: "Put message into local queue",
                                              900: STATUS_CODE_DESC_CMD_EXECUTED_SUCCESSFULLY},
                           STATUS_TAG_PULSE_TRIGGER: {100: "Detect new build, push tasks to Pulse MQ",
                                                      900: STATUS_CODE_DESC_CMD_EXECUTED_SUCCESSFULLY},
                           STATUS_TAG_PULSE_TRIGGER_BACKFILL: {100: "Push back fill task to Pulse MQ",
                                                               900: STATUS_CODE_DESC_CMD_EXECUTED_SUCCESSFULLY},
                           STATUS_TAG_SYNC_TASK_CONSUMER: {100: "Get queue message from sync queue",
                                                           900: STATUS_CODE_DESC_CMD_EXECUTED_SUCCESSFULLY},
                           STATUS_TAG_ASYNC_TASK_CONSUMER: {100: "Get queue message from async queue",
                                                            900: STATUS_CODE_DESC_CMD_EXECUTED_SUCCESSFULLY},
                           STATUS_TAG_SLACK: {100: "Get command from slack channel",
                                              200: "Put command into local queue",
                                              900: STATUS_CODE_DESC_CMD_EXECUTED_SUCCESSFULLY},
                           STATUS_TAG_INTERACTIVE: {100: "Get command from interactive mode",
                                                    200: "Put command into local queue",
                                                    300: "Execute scheduler realted command",
                                                    900: STATUS_CODE_DESC_CMD_EXECUTED_SUCCESSFULLY},
                           STATUS_TAG_GIT_RESET: STATUS_CODE_GENERAL_CMD_TEMPLATE,
                           STATUS_TAG_GIT_FETCH: STATUS_CODE_GENERAL_CMD_TEMPLATE,
                           STATUS_TAG_GIT_CHECKOUT: STATUS_CODE_GENERAL_CMD_TEMPLATE,
                           STATUS_TAG_GIT_PULL: STATUS_CODE_GENERAL_CMD_TEMPLATE,
                           STATUS_TAG_DOWNLOAD_NIGHTLY: {100: "Download specify nightly build, init download url",
                                                         200: "Download latest nightly build, init download url",
                                                         400: "Download build succssfully",
                                                         600: "Parse fx pkg json file successfully",
                                                         800: "Download build failed",
                                                         900: STATUS_CODE_DESC_CMD_EXECUTED_SUCCESSFULLY},
                           STATUS_TAG_DEPLOY_FIREFOX_PKG: {100: "Extract firefox package successfully",
                                                           200: "Extract firefox package failed",
                                                           300: "Link firefox package successfully",
                                                           900: STATUS_CODE_DESC_CMD_EXECUTED_SUCCESSFULLY},
                           STATUS_TAG_GENERATE_HASAL_CONFIG: {100: "Get Hasal repo path",
                                                              200: "Merge default and user input config into one object",
                                                              300: "Generate config path and content obj mapping",
                                                              400: "Generate runtest.py command parameters mapping",
                                                              900: STATUS_CODE_DESC_CMD_EXECUTED_SUCCESSFULLY},
                           STATUS_TAG_RUN_HASAL_RUNTEST_CMD: {100: "Init runtest cmd string",
                                                              900: STATUS_CODE_DESC_CMD_EXECUTED_SUCCESSFULLY},
                           STATUS_TAG_RUNTEST_CMD: {100: "Get case information",
                                                    200: "Case executed successfully, pass image compare, fps and sikuli round status validation also pass",
                                                    300: "Sikuli script running status",
                                                    500: "Case executed successfully",
                                                    600: "Case exec time",
                                                    700: "Cannot find result.json in local directory",
                                                    710: "Upload video failed",
                                                    720: "Case executed failed, check the failed detail in status content, compare_img_result should equal to pass image compare, fps_stat and round_status should equal to 0",
                                                    730: "Case executed failed, due to not able to find the stat file of hasal",
                                                    740: "Case executed failed, due to unknown exception happened",
                                                    830: "Loop test final status is failed",
                                                    840: "Upload to perfherder failed with error coce",
                                                    850: "Upload to perfherder failed due to unknown exception",
                                                    900: "Case execute successfully and upload to perfhderder successfully or upload option disabled"
                                                    }
                           }

    @staticmethod
    def get_status_folder():
        """
        Get status folder path and create folder if not exist
        @return: status folder path
        """
        default_hasal_repo_path = CommonUtil.auto_get_hasal_repo_path()
        status_folder_path = os.path.join(default_hasal_repo_path, StatusFileCreator.DEFAULT_STATUS_FOLDER_NAME)
        if not os.path.exists(status_folder_path):
            os.mkdir(status_folder_path)
        return status_folder_path

    @staticmethod
    def create_job_id_folder(input_job_name):
        """
        create job id folder
        @param input_job_name:
        @return: job id
        """
        # check status folder exist
        status_folder_path = StatusFileCreator.get_status_folder()
        utc_timestamp = CommonUtil.get_utc_now_timestamp()
        job_id = "%s-%s" % (input_job_name, utc_timestamp)
        job_id_folder_path = os.path.join(status_folder_path, job_id)

        if os.path.exists(job_id_folder_path):
            logger.error("Failed on creating job id folder due to job id duplicate, job_id_folder_path:[%s]" % job_id_folder_path)
            return None
        else:
            os.mkdir(job_id_folder_path)
            return job_id

    @staticmethod
    def get_status_code_desc(status_tag, status_code):
        if status_tag not in StatusFileCreator.STATUS_CODE_MAPPING:
            logger.error("Cannot find status tag[%s] in current status code mapping [%s]" % (status_tag, StatusFileCreator.STATUS_CODE_MAPPING))
        else:
            if status_code not in StatusFileCreator.STATUS_CODE_MAPPING[status_tag]:
                logger.error("Cannot find status code[%s] in current status tag dict [%s]" % (status_code, StatusFileCreator.STATUS_CODE_MAPPING[status_tag]))
            else:
                return StatusFileCreator.STATUS_CODE_MAPPING[status_tag][status_code]
        return None

    @staticmethod
    def create_status_file(status_file_folder, status_tag, status_code, status_content=None, allow_duplicate_status_file=True):
        """
        create status file, the status file format will be 123-xyz.json
        @param status_file_folder:
        @param status_tag:
        @param status_code: status code input here should reference to the StatusFileCreator.STATUS_CODE_MAPPING
        variable, you can find the detail desc in this variable about different code for different tag
        @param status_content:
        @return:
        """

        status_code_desc = StatusFileCreator.get_status_code_desc(status_tag, status_code)
        if status_code_desc:
            if not status_content:
                write_status_content = {"status_code_desc": status_code_desc,
                                        "utc_timestamp": str(CommonUtil.get_utc_now_timestamp())}
            else:
                if "status_code_desc" in status_content or "utc_timestamp" in status_content:
                    logger.error("Duplicate key[status_code_desc or utc_timestamp] in current status content keys [%s]" % status_content.keys())
                    return None
                else:
                    if isinstance(status_content, dict):
                        write_status_content = CommonUtil.mask_credential_value(copy.deepcopy(status_content))
                    else:
                        write_status_content = {"status_content": status_content}
                    write_status_content["status_code_desc"] = status_code_desc
                    write_status_content["utc_timestamp"] = str(CommonUtil.get_utc_now_timestamp())

            status_file_name = "%s-%s.json" % (status_code, status_tag)
            status_file_path = os.path.join(status_file_folder, status_file_name)
            if os.path.exists(status_file_folder):
                if os.path.exists(status_file_path):
                    if allow_duplicate_status_file:
                        exist_status_file_list = [int(current_status_fn.split("-")[1]) for current_status_fn in os.listdir(status_file_folder) if current_status_fn.split("-")[0] == str(status_code) and current_status_fn.split("-")[-1].split(os.extsep)[0] == str(status_tag) and len(current_status_fn.split(os.extsep)[0].split("-")) == 3]
                        exist_status_file_list.sort()
                        if len(exist_status_file_list) > 0:
                            duplicate_number = exist_status_file_list[-1] + 1
                        else:
                            duplicate_number = 1
                        new_status_file_name = "%s-%s-%s.json" % (status_code, duplicate_number, status_tag)
                        new_status_file_path = os.path.join(status_file_folder, new_status_file_name)
                        with open(new_status_file_path, "wb") as fh:
                            json.dump(write_status_content, fh)
                        return new_status_file_path
                    else:
                        logger.error("Failed to create status file due to status file path duplicate, status file path [%s]" % status_file_path)
                else:
                    with open(status_file_path, "wb") as fh:
                        json.dump(write_status_content, fh)
                    return status_file_path
            else:
                logger.error("Failed to create status file due to status file folder not exist, status file folder [%s]" % status_file_folder)
            return None
        else:
            logger.error("Cannot find corresponding desc for current status tag[%s] and status code[%s]" % (status_tag, status_code))
            return None
