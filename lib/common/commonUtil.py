import os
import re
import json
import platform
import subprocess
import numpy as np
from datetime import datetime
from environment import Environment
from logConfig import get_logger

logger = get_logger(__name__)


class StatusRecorder(object):
    # Result for STATUS_IMG_COMPARE_RESULT
    PASS_IMG_COMPARE_RESULT = "PASS_IMG_COMPARE_RESULT"
    ERROR_EVENT_IMAGE_LESS_THAN_2 = "ERROR_EVENT_IMAGE_LESS_THAN_2"
    ERROR_EVENT_IMAGE_BOTH_SAME = "ERROR_EVENT_IMAGE_BOTH_SAME"
    ERROR_MISSING_FIELD_IMG_COMPARE_RESULT = "ERROR_MISSING_FIELD_IMG_COMPARE_RESULT"

    ERROR_CANT_FIND_STATUS_FILE = "ERROR_CANT_FIND_STATUS_FILE"
    ERROR_FPS_STAT_ABNORMAL = "ERROR_FPS_STAT_ABNORMAL"
    ERROR_ROUND_STAT_ABNORMAL = "ERROR_ROUND_STAT_ABNORMAL"
    ERROR_COMPARING_IMAGE_FAILED = "ERROR_COMPARING_IMAGE_FAILED"
    ERROR_LOOP_TEST_RAISE_EXCEPTION = "ERROR_LOOP_TEST_RAISE_EXCEPTION"

    ERROR_COMPARE_RESULT_IS_NONE = "ERROR_COMPARE_RESULT_IS_NONE"

    STATUS_IMG_COMPARE_RESULT = "status_img_compare_result"
    STATUS_SIKULI_RUNNING_VALIDATION = "sikuli_running_stat"
    STATUS_FPS_VALIDATION = "fps_stat"
    STATUS_TIME_LIST_COUNTER = "time_list_counter"
    STATUS_VALIDATOR_RESULT = "validator_result"

    STATUS_FPS_VALIDATION_NORMAL = 0
    STATUS_FPS_VALIDATION_ABNORMAL = 1

    def __init__(self, status_fp):
        self.status_fp = status_fp
        self.current_status = CommonUtil.load_json_file(status_fp)

    def get_current_status(self):
        return self.current_status['current_status']

    def record_current_status(self, input_status_dict):
        self.current_status = CommonUtil.load_json_file(self.status_fp)
        if 'current_status' in self.current_status:
            self.current_status['current_status'].update(input_status_dict)
        else:
            self.current_status['current_status'] = input_status_dict
        with open(self.status_fp, "w+") as fh:
            json.dump(self.current_status, fh)

    def record_status(self, case_name, status, value):
        self.current_status = CommonUtil.load_json_file(self.status_fp)
        if case_name in self.current_status:
            self.current_status[case_name].append(
                {'time_seq': datetime.strftime(datetime.now(), '%Y%m%d%H%M%S'), 'status': status, 'value': value})
        else:
            self.current_status[case_name] = [
                {'time_seq': datetime.strftime(datetime.now(), '%Y%m%d%H%M%S'), 'status': status, 'value': value}]
        with open(self.status_fp, "w+") as fh:
            json.dump(self.current_status, fh)


class CalculationUtil(object):

    @staticmethod
    def runtime_calculation_event_point_base(input_running_time_result):
        run_time = -1
        comparing_time_data = {}
        for event_data in input_running_time_result:
            for time_point in ['start', 'end']:
                if time_point in event_data:
                    comparing_time_data[time_point] = event_data['time_seq']
                    break
        event_time_dict = dict()
        if len(comparing_time_data.keys()) == 2:
            run_time = comparing_time_data['end'] - comparing_time_data['start']
            if run_time > 0:
                for event_data in input_running_time_result:
                    for event_name in event_data:
                        if event_name != 'time_seq' and event_name != 'start' and event_name != 'end':
                            event_time_dict[event_name] = np.absolute(
                                event_data['time_seq'] - comparing_time_data['start'])
        return run_time, event_time_dict

    @staticmethod
    def Q_MooreMcCabe(seq):
        seq_len = len(seq)
        if seq_len % 2:
            if (seq_len + 1) % 4:
                Q1 = float((seq[(seq_len + 1) / 4] + seq[(seq_len + 1) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 1) / 4 - 1])
            if (3 * seq_len + 3) % 4:
                Q3 = float((seq[(3 * seq_len + 3) / 4] + seq[(3 * seq_len + 3) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 3) / 4 - 1])
        else:
            if (seq_len + 2) % 4:
                Q1 = float((seq[(seq_len + 2) / 4] + seq[(seq_len + 2) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 2) / 4 - 1])
            if (3 * seq_len + 2) % 4:
                Q3 = float((seq[(3 * seq_len + 2) / 4] + seq[(3 * seq_len + 2) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 2) / 4 - 1])
        return [Q1, Q3]

    @staticmethod
    def Q_Tukey(seq):
        seq_len = len(seq)
        if seq_len % 2:
            if (seq_len + 1) % 4:
                Q1 = float((seq[(seq_len + 3) / 4] + seq[(seq_len + 3) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 3) / 4 - 1])
            if (3 * seq_len + 3) % 4:
                Q3 = float((seq[(3 * seq_len + 1) / 4] + seq[(3 * seq_len + 1) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 1) / 4 - 1])
        else:
            if (seq_len + 2) % 4:
                Q1 = float((seq[(seq_len + 2) / 4] + seq[(seq_len + 2) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 2) / 4 - 1])
            if (3 * seq_len + 2) % 4:
                Q3 = float((seq[(3 * seq_len + 2) / 4] + seq[(3 * seq_len + 2) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 2) / 4 - 1])
        return [Q1, Q3]

    @staticmethod
    def Q_FreundPerles(seq):
        seq_len = len(seq)
        if seq_len % 2:
            if (seq_len + 1) % 4:
                Q1 = float((seq[(seq_len + 3) / 4] + seq[(seq_len + 3) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 3) / 4 - 1])
            if (3 * seq_len + 3) % 4:
                Q3 = float((seq[(3 * seq_len + 1) / 4] + seq[(3 * seq_len + 1) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 1) / 4 - 1])
        else:
            if (seq_len + 2) % 4:
                Q1 = float((seq[(seq_len + 3) / 4] + seq[(seq_len + 3) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 3) / 4 - 1])
            if (3 * seq_len + 2) % 4:
                Q3 = float((seq[(3 * seq_len + 1) / 4] + seq[(3 * seq_len + 1) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 1) / 4 - 1])
        return [Q1, Q3]

    @staticmethod
    def Q_Minitab(seq):
        seq_len = len(seq)
        if seq_len % 2:
            if (seq_len + 1) % 4:
                Q1 = float((seq[(seq_len + 1) / 4] + seq[(seq_len + 1) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 1) / 4 - 1])
            if (3 * seq_len + 3) % 4:
                Q3 = float((seq[(3 * seq_len + 3) / 4] + seq[(3 * seq_len + 3) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 3) / 4 - 1])
        else:
            if (seq_len + 2) % 4:
                Q1 = float((seq[(seq_len + 1) / 4] + seq[(seq_len + 1) / 4 - 1])) / 2
            else:
                Q1 = float(seq[(seq_len + 1) / 4 - 1])
            if (3 * seq_len + 2) % 4:
                Q3 = float((seq[(3 * seq_len + 3) / 4] + seq[(3 * seq_len + 3) / 4 - 1])) / 2
            else:
                Q3 = float(seq[(3 * seq_len + 3) / 4 - 1])
        return [Q1, Q3]

    @staticmethod
    def drop_outlier_value(seq, outliers):
        for outlier in outliers:
            seq.remove(outlier)
        return seq

    @staticmethod
    def remove_outlier(input_list, key_name, method=1):
        outliers = []
        outliers_value = []
        sorted_list = sorted(input_list, key=lambda k: k[key_name])
        seq_value = [d[key_name] for d in sorted_list]
        if len(input_list) >= 3:
                # Default using Moore and McCabe method to calculate quartile value
                Q_Calculation = {
                    '1': CalculationUtil.Q_MooreMcCabe,
                    '2': CalculationUtil.Q_Tukey,
                    '3': CalculationUtil.Q_FreundPerles,
                    '4': CalculationUtil.Q_Minitab
                }
                [Q1, Q3] = Q_Calculation.setdefault(str(method), CalculationUtil.Q_MooreMcCabe)(seq_value)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                for data in sorted_list:
                    if data[key_name] < lower or data[key_name] > upper:
                        outliers.append(data)
                        outliers_value.append(data[key_name])
                sorted_list = CalculationUtil.drop_outlier_value(sorted_list, outliers)
        return sorted_list, outliers

    @staticmethod
    def get_median_avg_sigma_value(input_list, key_name):
        sorted_list = sorted(input_list, key=lambda k: k[key_name])
        seq_value = [d[key_name] for d in sorted_list]
        if len(sorted_list) == 0:
            median_time_index = 0
            mean = 0
            median = 0
            sigma = 0
            min = 0
            max = 0
        elif len(sorted_list) == 1:
            median_time_index = 0
            mean = float(sorted_list[median_time_index][key_name])
            median = float(sorted_list[median_time_index][key_name])
            sigma = 0
            min = seq_value[0]
            max = seq_value[0]
        else:
            if len(sorted_list) % 2:
                median_time_index = (len(input_list) - 1) / 2
                median = float(sorted_list[median_time_index][key_name])
                mean = np.mean(seq_value)
                sigma = np.std(seq_value)
            else:
                median_time_index = len(input_list) / 2 - 1
                median = float(sorted_list[median_time_index][key_name] + sorted_list[median_time_index + 1][key_name]) / 2
                mean = np.mean(seq_value)
                sigma = np.std(seq_value)
            min = seq_value[0]
            max = seq_value[-1]
        return sorted_list, median_time_index, median, mean, sigma, min, max

    @staticmethod
    def generate_statistics_value_for_server(input_list, enable_remove_outlier=True):
        if enable_remove_outlier:
            tmp_list, outliers = CalculationUtil.remove_outlier(input_list, 'run_time')
        else:
            outliers = []
            tmp_list = input_list
        sorted_list, median_time_index, median_value, mean_value, sigma_value, min_value, max_value = CalculationUtil.get_median_avg_sigma_value(tmp_list, 'run_time')
        if len(sorted_list) % 2:
            si_value = input_list[median_time_index]['si']
            psi_value = input_list[median_time_index]['psi']
        else:
            si_value = (input_list[median_time_index]['si'] + input_list[median_time_index + 1]['si']) / 2
            psi_value = (input_list[median_time_index]['psi'] + input_list[median_time_index + 1]['psi']) / 2
        return mean_value, median_value, sigma_value, tmp_list, outliers, si_value, psi_value


class CommonUtil(object):

    RECORDER_LIST = [Environment.PROFILER_FLAG_AVCONV, Environment.PROFILER_FLAG_OBS]
    logger = get_logger(__file__)

    @staticmethod
    def get_username():
        """
        Get current username.
        The UNIX platform will return the value of `pwd.getpwuid(os.getuid()).pw_name`.
        The Windows platform will return 'USERNAME' of environ, or default username `user`.
        @return: current username.
        """
        if platform.system().lower() == 'windows':
            username = os.environ.get('USERNAME')
            if not username:
                # default user name
                username = 'user'
        else:
            import pwd
            username = pwd.getpwuid(os.getuid()).pw_name
        return username

    @staticmethod
    def get_appdata_dir():
        """
        Get current user's AppData folder.

        Availability: Windows.
        @return: current user's AppData folder.
        """
        if platform.system().lower() == 'windows':
            appdata_path = os.environ.get('APPDATA')
            if not appdata_path:
                # default user APPDATA folder
                appdata_path = r'C:\Users\{username}\AppData\Roaming'.format(username=CommonUtil.get_username())
        else:
            logger.error('Doesn\'t support get APPDATA at platform {}.'.format(platform.system()))
            appdata_path = ''
        return appdata_path

    @staticmethod
    def get_user_dir():
        """
        Get current user's home folder.
        The UNIX platform will return the value of `pwd.getpwuid(os.getuid()).pw_dir`.
        The Windows platform will return 'USERPROFILE' of environ.
        @return: current user's home folder.
        """
        if platform.system().lower() == 'windows':
            user_dir = os.environ.get('USERPROFILE')
            if not user_dir:
                # default user dir
                user_dir = r'C:\Users\{username}'.format(username=CommonUtil.get_username())
        else:
            import pwd
            user_dir = pwd.getpwuid(os.getuid()).pw_dir
        return user_dir

    @staticmethod
    def execute_runipy_cmd(input_template_fp, output_ipynb_fp, **kwargs):
        default_runipy_cmd = 'runipy'
        ipynb_env = os.environ.copy()
        for variable_name in kwargs.keys():
            ipynb_env[variable_name] = str(kwargs[variable_name])
        cmd_list = [default_runipy_cmd, input_template_fp, output_ipynb_fp]
        return subprocess.call(cmd_list, env=ipynb_env)

    @staticmethod
    def get_mac_os_display_channel():
        if platform.system().lower() == "darwin":
            proc = subprocess.Popen(
                ['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', '""'],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout = proc.stdout.read()
            if "Capture screen" in stdout:
                display_channel = stdout[stdout.index('Capture screen') - 3]
                if display_channel in [str(i) for i in range(10)]:
                    return display_channel
            return "1"
        else:
            return ":0.0"

    @staticmethod
    def load_json_file(fp):
        if os.path.exists(fp):
            with open(fp) as fh:
                return json.load(fh)
        else:
            return {}

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
