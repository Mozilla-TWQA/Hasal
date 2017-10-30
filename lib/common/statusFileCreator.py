import os
import copy
import json
from commonUtil import CommonUtil
from logConfig import get_logger
logger = get_logger(__name__)


class StatusFileCreator(object):
    DEFAULT_STATUS_FOLDER_NAME = "status"

    STATUS_TAG_PULSE = "pulse"
    STATUS_TAG_SLACK = "slack"
    STATUS_TAG_INTERACTIVE = "interactive"
    STATUS_TAG_SYNC_TASK_CONSUMER = "sync_task_consumer"
    STATUS_TAG_ASYNC_TASK_CONSUMER = "async_task_consumer"

    STATUS_CODE_MAPPING = {STATUS_TAG_PULSE: {100: "Get message from pulse queue",
                                              200: "Put message into local queue",
                                              900: "Successfully complete"},
                           STATUS_TAG_SYNC_TASK_CONSUMER: {100: "Get queue message from sync queue",
                                                           900: "Successfully complete"},
                           STATUS_TAG_ASYNC_TASK_CONSUMER: {100: "Get queue message from async queue",
                                                            900: "Successfully complete"},
                           STATUS_TAG_SLACK: {100: "Get command from slack channel",
                                              200: "Put command into local queue",
                                              900: "Successfully complete"},
                           STATUS_TAG_INTERACTIVE: {100: "Get command from interactive mode",
                                                    200: "Put command into local queue",
                                                    300: "Execute scheduler realted command",
                                                    900: "Successfully complete"}
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
    def create_status_file(status_file_folder, status_tag, status_code, status_content=None):
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
                    write_status_content = CommonUtil.mask_credential_value(copy.deepcopy(status_content))
                    write_status_content["status_code_desc"] = status_code_desc
                    write_status_content["utc_timestamp"] = str(CommonUtil.get_utc_now_timestamp())

            status_file_name = "%s-%s.json" % (status_code, status_tag)
            status_file_path = os.path.join(status_file_folder, status_file_name)
            if os.path.exists(status_file_folder):
                if os.path.exists(status_file_path):
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
