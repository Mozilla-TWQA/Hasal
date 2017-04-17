import os
import re
import json
from datetime import datetime
from environment import Environment


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

    @staticmethod
    def is_video_recording(settings):
        """
        Checking the Video Recording settings.
        @return: True if there is one Recorder, False if there is no Recorder. Raise exception when there are multiple Recorders.
        """
        recording_flags = {Environment.PROFILER_FLAG_AVCONV: False}
        for k in recording_flags.keys():
            v = settings.get(k, {})
            if v:
                is_enabled = v.get('enable', False)
                recording_flags[k] = is_enabled

        recording_enable_amount = sum(map(bool, recording_flags.values()))
        if recording_enable_amount == 0:
            return False, recording_flags
        elif recording_enable_amount == 1:
            return True, recording_flags
        elif recording_enable_amount > 1:
            raise Exception('More than one video recorders are enabled.\n{}'.format(recording_flags))
