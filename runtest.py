"""runtest.

Usage:
  runtest.py [--exec-config=<str>] [--firefox-config=<str>] [--index-config=<str>] [--online-config=<str>] [--global-config=<str>]
  runtest.py (-h | --help)

Options:
  -h --help                       Show this screen.
  --exec-config=<str>             Specify the test execution config file; max-run, max-retry, advance, keep-browser etc. settings can be controlled in here. [default: configs/exec/default.json]
  --firefox-config=<str>          Specify the test Firefox config file; [default: configs/firefox/default.json]
  --index-config=<str>            Specify the index config file; you can specify which index you want to generate here. [default: configs/index/runtimeDctGenerator.json]
  --online-config=<str>           Specify the online config file; you can specify if you want to enable online data submission and other related settings here. [default: configs/online/default.json]
  --global-config=<str>           Specify the global config file; you can modify the output fn and status fn here. [default: configs/global/default.json]

"""
import os
import json
import copy
import shutil
import platform
import subprocess
from docopt import docopt
from datetime import datetime
from lib.common.commonUtil import load_json_file
from lib.common.commonUtil import StatusRecorder
from lib.common.commonUtil import CommonUtil
from lib.helper.uploadAgentHelper import UploadAgent
from lib.common.logConfig import get_logger
from lib.helper.firefoxProfileCreator import FirefoxProfileCreator

if platform.system().lower() == "linux":
    DEFAULT_TASK_KILL_LIST = ["ffmpeg", "firefox", "chrome"]
    DEFAULT_TASK_KILL_CMD = "pkill "
    DEFAULT_EDITOR_CMD = "cat "
elif platform.system().lower() == "windows":
    DEFAULT_TASK_KILL_CMD = "taskkill /f /t /im "
    DEFAULT_TASK_KILL_LIST = ["ffmpeg", "firefox.exe", "chrome.exe", "obs32.exe", "obs64.exe"]
    DEFAULT_EDITOR_CMD = "type "
else:
    DEFAULT_TASK_KILL_LIST = ["ffmpeg", "firefox", "chrome"]
    DEFAULT_TASK_KILL_CMD = "pkill "
    DEFAULT_EDITOR_CMD = "open -e "


class RunTest(object):
    def __init__(self, **kwargs):
        self.exec_config = {}
        self.online_config = {}
        self.index_config = {}
        self.global_config = {}
        self.firefox_config = {}
        # load exec-config, firefox-config, index-config, online-config and global config to self object
        self.exec_config_fp = os.path.abspath(kwargs['exec_config'])
        self.firefox_config_fp = os.path.abspath(kwargs['firefox_config'])
        self.index_config_fp = os.path.abspath(kwargs['index_config'])
        self.online_config_fp = os.path.abspath(kwargs['online_config'])
        self.global_config_fp = os.path.abspath(kwargs['global_config'])
        for variable_name in kwargs.keys():
            setattr(self, variable_name, load_json_file(kwargs[variable_name]))

        # init logger
        self.logger = get_logger(__file__, self.exec_config['advance'])

        self.logger.debug('\n###############\n#  Important  #\n###############\n')
        for v_name in kwargs.keys():
            self.logger.debug(
                'Loading Settings from {}:\n{}\n'.format(v_name, json.dumps(getattr(self, v_name), indent=4)))

        # init values
        self.firefox_profile_creator = FirefoxProfileCreator()
        self.settings_prefs = self.firefox_config.get('prefs', {})
        self.cookies_settings = self.firefox_config.get('cookies', {})
        self.extensions_settings = self.firefox_config.get('extensions', {})
        self.suite_result_dp = ''
        self._firefox_profile_path = self.firefox_profile_creator.get_firefox_profile(
            prefs=self.settings_prefs,
            cookies_settings=self.cookies_settings,
            extensions_settings=self.extensions_settings)
        self.default_result_fp = os.path.join(os.getcwd(), self.global_config['default-result-fn'])

        # check the video recording, raise exception if more than one recorders
        CommonUtil.is_video_recording(self.firefox_config)

    def suite_setup(self):
        upload_dir = os.path.join(os.getcwd(), self.global_config['default-case-complete-artifact-store-dn'])
        date_seq_id = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
        self.suite_result_dp = os.path.join(upload_dir, date_seq_id)
        if os.path.exists(upload_dir):
            if not os.path.exists(self.suite_result_dp):
                os.mkdir(self.suite_result_dp)
        else:
            os.mkdir(upload_dir)
            os.mkdir(self.suite_result_dp)

        if self.online_config['enable']:
            self.upload_agent_obj = UploadAgent(svr_config=self.online_config['svr-config'], test_comment=self.exec_config['comment'])

    def suite_teardown(self):
        if self.online_config['enable']:
            self.clean_up_output_data()
        if self.exec_config['advance']:
            self.logger.debug('Skip removing profile: {}'.format(self._firefox_profile_path))
        elif os.path.isdir(self._firefox_profile_path):
            self.firefox_profile_creator.remove_firefox_profile()
        if os.path.exists(self.default_result_fp):
            shutil.copy(self.default_result_fp, self.suite_result_dp)
        os.system(DEFAULT_EDITOR_CMD + " end.txt")

    def case_setup(self):
        if self.online_config['enable'] and os.path.exists(self.default_result_fp):
            os.remove(self.default_result_fp)

    def case_teardown(self, data):
        if self.online_config['enable']:
            if self.online_config['perfherder-revision']:
                self.upload_agent_obj.upload_register_data(self.exec_config['exec-suite-fp'],
                                                           self.index_config['case-type'],
                                                           self.online_config['perfherder-suitename'])
            self.upload_agent_obj.upload_videos(data)

    def kill_legacy_process(self):
        for process_name in DEFAULT_TASK_KILL_LIST:
            cmd_str = DEFAULT_TASK_KILL_CMD + process_name
            os.system(cmd_str)

    def clean_up_output_data(self):
        # clean output folder
        output_dir = os.path.join(os.getcwd(), self.global_config['default-case-temp-artifact-store-dn'])
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    def get_test_env(self, **kwargs):
        result = os.environ.copy()
        result['EXEC_CONFIG_FP'] = self.exec_config_fp
        result['INDEX_CONFIG_FP'] = self.index_config_fp
        result['GLOBAL_CONFIG_FP'] = self.global_config_fp
        result['FIREFOX_CONFIG_FP'] = self.firefox_config_fp
        result['ONLINE_CONFIG_FP'] = self.online_config_fp
        result['SUITE_RESULT_DP'] = str(self.suite_result_dp)
        result['FIREFOX_PROFILE_PATH'] = self._firefox_profile_path

        if self.online_config['perfherder-revision']:
            result['PERFHERDER_REVISION'] = self.online_config['perfherder-revision']
        else:
            result['PERFHERDER_REVISION'] = ""
        if self.online_config['perfherder-pkg-platform']:
            result['PERFHERDER_PKG_PLATFORM'] = self.online_config['perfherder-pkg-platform']
        else:
            result['PERFHERDER_PKG_PLATFORM'] = ""
        for variable_name in kwargs.keys():
            result[variable_name] = str(kwargs[variable_name])
        return result

    def run_test_result_analyzer(self, test_case_module_name, test_name, current_run, current_retry, video_result):
        run_result = None
        objStatusRecorder = StatusRecorder(self.global_config['default-running-statistics-fn'])
        if os.path.exists(self.global_config['default-current-running-status-fn']):
            with open(self.global_config['default-current-running-status-fn']) as stat_fh:
                run_result = json.load(stat_fh)
                round_status = int(run_result.get("round_status", -1))
                fps_stat = int(run_result.get("fps_stat", -1))
                if round_status == 0 and fps_stat == 0:
                    if self.online_config['enable']:
                        # Online mode handling
                        upload_result = self.upload_agent_obj.upload_result(self.default_result_fp)
                        if upload_result:
                            self.logger.info("===== upload success =====")
                            self.logger.info(upload_result)
                            video_result['ip'] = upload_result['ip']
                            video_result['video_path'] = upload_result['video']
                            video_result['test_name'] = test_name
                            self.logger.info("===== upload success =====")
                            if "current_test_times" in upload_result:
                                current_run = upload_result["current_test_times"]
                                self.exec_config['max-run'] = upload_result['config_test_times']
                            else:
                                current_run += 1
                        else:

                            current_run += 1
                    else:
                        if run_result.get("comparing_image_missing", False):
                            if "time_list_counter" in run_result:
                                current_run = int(run_result['time_list_counter'])
                            else:
                                current_run += 1
                        else:
                            objStatusRecorder.record_status(test_case_module_name, StatusRecorder.ERROR_COMPARING_IMAGE_FAILED, None)
                            current_retry += 1
                else:
                    if round_status != 0:
                        objStatusRecorder.record_status(test_case_module_name, StatusRecorder.ERROR_ROUND_STAT_ABNORMAL,
                                                        round_status)
                    if fps_stat != 0:
                        objStatusRecorder.record_status(test_case_module_name, StatusRecorder.ERROR_FPS_STAT_ABNORMAL,
                                                        round_status)
                    current_retry += 1
        else:
            self.logger.error("test could raise exception during execution!!")
            objStatusRecorder.record_status(test_case_module_name, StatusRecorder.ERROR_CANT_FIND_STATUS_FILE, None)
            current_retry += 1
        return current_run, current_retry, video_result

    def loop_test(self, test_case_module_name, test_name, test_env, current_run=0, current_retry=0):
        return_result = {"ip": None, "video_path": None, "test_name": None}
        while current_run < self.exec_config['max-run']:
            self.logger.info("The counter is %d and the retry counter is %d" % (current_run, current_retry))
            try:
                self.kill_legacy_process()
                self.run_test(test_case_module_name, test_env)
                current_run, current_retry, return_result = self.run_test_result_analyzer(test_case_module_name,
                                                                                          test_name, current_run,
                                                                                          current_retry, return_result)
            except Exception as e:
                self.logger.warn('Exception happend during running test!')
                objStatusRecorder = StatusRecorder(self.global_config['default-running-statistics-fn'])
                objStatusRecorder.record_status(test_case_module_name, StatusRecorder.ERROR_LOOP_TEST_RAISE_EXCEPTION, e)
                current_retry += 1

            if current_retry >= self.exec_config['max-retry']:
                break
        return return_result

    def run_test(self, test_case_module_name, test_env):
        self.logger.debug("========== Environment data ======")
        self.logger.debug(test_env)
        self.logger.debug("========== Environment data ======")
        self.logger.info(" ".join(["python", "-m", "unittest", test_case_module_name]))
        subprocess.call(["python", "-m", "unittest", test_case_module_name], env=test_env)

    def suite_validator(self):
        exec_case_list = []
        with open(self.exec_config['exec-suite-fp']) as exec_suite_fh:
            exec_case_list = exec_suite_fh.read().splitlines()
        supported_case_list = copy.deepcopy(exec_case_list)
        if self.index_config['supported-suite-fp'] != "":
            with open(self.index_config['supported-suite-fp']) as supported_suite_fh:
                supported_case_list = supported_suite_fh.read().splitlines()
        for exec_case_path in exec_case_list:
            if exec_case_path not in supported_case_list:
                return False
        return True

    def loop_suite(self):
        if self.suite_validator():
            with open(self.exec_config['exec-suite-fp']) as input_suite_fh:
                for test_case in input_suite_fh.read().splitlines():
                    if test_case:
                        # case setup
                        self.case_setup()

                        # case run
                        runtime_case_data = {}
                        test_case_module_name = ""
                        test_case_fp = ""
                        test_env = None
                        test_name = ""
                        if self.index_config['case-type'] == "pt":
                            test_case_module_name = "%s.%s" % (self.global_config['default-test-dn'], "test_pilot_run")
                            runtime_case_data["SIKULI_SCRIPT_PATH"] = test_case
                            runtime_case_data["TEST_SCRIPT_PY_DIR_PATH"] = os.sep.join(test_case_module_name.split(".")[:-1])
                            if test_case.endswith(os.sep):
                                test_name = test_case.split(os.sep)[-2].split(".")[0]
                            else:
                                test_name = test_case.split(os.sep)[-1].split(".")[0]
                            test_case_fp = test_case
                        else:
                            test_case_fp = test_case.replace(".", os.sep) + ".py"
                            test_name = test_case.split(".")[-1]
                            test_case_module_name = test_case
                            runtime_case_data["TEST_SCRIPT_PY_DIR_PATH"] = os.sep.join(test_case.split(".")[:-1])
                            # if webdriver is enable, we need to get parameters for running browsers
                            if not os.path.exists(test_case_fp):
                                self.logger.error("Test script [%s] is not exist!" % test_case_fp)
                                continue
                            if self.exec_config['user-simulation-tool'] == self.global_config['default-user-simulation-tool-webdriver']:
                                runtime_case_data['webdriver'] = "True"
                                for browser_type in self.exec_config['webdriver-run-browser']:
                                    runtime_case_data['browser_type'] = browser_type
                                    test_env = self.get_test_env(**runtime_case_data)
                                    data = self.loop_test(test_case_module_name, test_name, test_env)
                                    self.case_teardown(data)
                            else:
                                test_env = self.get_test_env(**runtime_case_data)
                                data = self.loop_test(test_case_module_name, test_name, test_env)
                                self.case_teardown(data)

        else:
            self.logger.error("Current suite file [%s] contains test cases which are not supported." % self.exec_config['exec-suite-fp'])

    def run(self):
        self.suite_setup()
        self.loop_suite()
        self.suite_teardown()


def main():
    arguments = docopt(__doc__)
    run_test_obj = RunTest(exec_config=arguments['--exec-config'], firefox_config=arguments['--firefox-config'],
                           index_config=arguments['--index-config'], online_config=arguments['--online-config'],
                           global_config=arguments['--global-config'])
    run_test_obj.run()

if __name__ == '__main__':
    main()
