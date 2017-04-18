import os
import re
import json
from datetime import datetime
from environment import Environment
from logConfig import get_logger


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

    RECORDER_LIST = [Environment.PROFILER_FLAG_AVCONV, ]
    logger = get_logger(__file__)

    @staticmethod
    def atoi(text):
        return int(text) if text.isdigit() else text

    @classmethod
    def natural_keys(cls, text):
        return [cls.atoi(c) for c in re.split('(\d+)', text)]

    @staticmethod
    def _find_recorder_stat(total_recorder_settings):
        recorder_name_list = []
        total_recorder_flags = dict((item, False) for item in CommonUtil.RECORDER_LIST)
        for k in total_recorder_flags.keys():
            v = total_recorder_settings.get(k, {})
            if v:
                is_enabled = v.get('enable', False)
                total_recorder_flags[k] = is_enabled
                if is_enabled:
                    recorder_name_list.append(k)
        CommonUtil.logger.debug('Enabled Recorders: {}'.format(recorder_name_list))
        return recorder_name_list, total_recorder_flags

    @staticmethod
    def is_video_recording(settings):
        """
        Checking the Video Recording settings.
        @return: True if there is one Recorder, False if there is no Recorder. Raise exception when there are multiple Recorders.
        """
        # TODO: load recorder settings from firefox_config now, it might be changed...
        total_recorder_settings = settings.get('extensions', {})

        recorder_name_list, total_recorder_flags = CommonUtil._find_recorder_stat(total_recorder_settings)

        recording_enable_amount = sum(map(bool, total_recorder_flags.values()))
        if recording_enable_amount == 0:
            CommonUtil.logger.info('No Recorder.')
            return False
        elif recording_enable_amount == 1:
            CommonUtil.logger.info('Enabled Recorder: {}'.format(recorder_name_list[0]))
            return True
        elif recording_enable_amount > 1:
            CommonUtil.logger.error('More than one Recorder.')
            raise Exception('More than one video recorders are enabled.\n{}'.format(total_recorder_flags))

    @staticmethod
    def is_validate_fps(settings):
        """
        Checking the FPS validation settings.
        @return: True if FPS validation is enabled, False if FPS validation is disabled
        """
        try:
            if CommonUtil.is_video_recording(settings):
                total_recorder_settings = settings.get('extensions', {})

                recorder_name_list, _ = CommonUtil._find_recorder_stat(total_recorder_settings)

                if len(recorder_name_list) == 1:
                    recorder_name = recorder_name_list[0]
                    recorder_setting = total_recorder_settings.get(recorder_name, {})
                    is_validate_fps = recorder_setting.get('validate-fps', False)
                    CommonUtil.logger.info('The validate-fps of {} Recorder: {}.'.format(recorder_name, is_validate_fps))
                    return is_validate_fps
                else:
                    return False
            else:
                return False
        except:
            return False
