import os
import re
import json
from datetime import datetime


def load_json_file(fp):
    if os.path.exists(fp):
        with open(fp) as fh:
            return json.load(fh)
    else:
        return {}


class StatusRecorder(object):
    ERROR_CANT_FIND_STATUS_FILE = "ERROR_CANT_FIND_STATUS_FILE"
    ERROR_FPS_STAT_ABNORMAL = "ERROR_FPS_STAT_ABNORMAL"
    ERROR_ROUND_STAT_ABNORMAL = "ERROR_ROUND_STAT_ABNORMAL"
    ERROR_COMPARING_IMAGE_FAILED = "ERROR_COMPARING_IMAGE_FAILED"
    ERROR_LOOP_TEST_RAISE_EXCEPTION = "ERROR_LOOP_TEST_RAISE_EXCEPTION"

    def __init__(self, status_fp):
        self.status_fp = status_fp
        self.current_status = load_json_file(status_fp)

    def record_status(self, case_name, status, value):
        if case_name in self.current_status:
            self.current_status[case_name].append(
                {'time_seq': datetime.strftime(datetime.now(), '%Y%m%d%H%M%S'), 'status': status, 'value': value})
        else:
            self.current_status[case_name] = [
                {'time_seq': datetime.strftime(datetime.now(), '%Y%m%d%H%M%S'), 'status': status, 'value': value}]
        with open(self.status_fp, "w+") as fh:
            json.dump(self.current_status, fh)

class CommonUtil(object):
    @staticmethod
    def atoi(text):
        return int(text) if text.isdigit() else text

    @classmethod
    def natural_keys(cls, text):
        return [cls.atoi(c) for c in re.split('(\d+)', text)]
