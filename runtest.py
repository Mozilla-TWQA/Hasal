"""runtest.

Usage:
  runtest.py re <suite.txt> [--online] [--online-config=<str>] [--max-run=<int>] [--max-retry=<int>] [--keep-browser] [--calc-si] [--profiler=<str>] [--comment=<str>] [--advance] [--waveform] [--perfherder-revision=<str>] [--perfherder-pkg-platform=<str>] [--jenkins-build-no=<int>]
  runtest.py pt <suite.txt> [--online] [--online-config=<str>] [--max-run=<int>] [--max-retry=<int>] [--keep-browser] [--calc-si] [--profiler=<str>] [--comment=<str>] [--advance] [--waveform] [--perfherder-revision=<str>] [--perfherder-pkg-platform=<str>] [--jenkins-build-no=<int>]
  runtest.py (-h | --help)

Options:
  -h --help                       Show this screen.
  --max-run=<int>                 Test run max no [default: 30].
  --max-retry=<int>               Test failed retry max no [default: 15].
  --keep-browser                  Keep the browser open after test script executed
  --calc-si                       Calculate the speed index (si) and perceptual speed index (psi)
  --profiler=<str>                Enabled profiler, current support profiler:avconv,geckoprofiler,harexport,chrometracing,fxall,justprofiler,mitmdump,fxtracelogger [default: avconv]
  --online                        Result will be transfer to server, calculated by server
  --online-config=<str>           Online server config [default: svrConfig.json]
  --comment=<str>                 Tag the comment on this test [default: <today>]
  --advance                       Only for expert user
  --waveform                      Waveform generated after case finished
  --perfherder-revision=<str>     Revision for upload to perfherder
  --perfherder-pkg-platform=<str> Package platform for upload to perfherder
  --jenkins-build-no=<int>        Jenkins build no [default: 0].

"""
import os
import json
import time
import shutil
import platform
import subprocess
from lib.helper.uploadAgentHelper import UploadAgent
from docopt import docopt
from lib.common.logConfig import get_logger

DEFAULT_RESULT_FP = "./result.json"
DEFAULT_TEST_FOLDER = "tests"
DEFAULT_RUNNING_STAT_FN = "stat.json"
DEFAULT_ERROR_CASE_LIST = "error_case_list.txt"

if platform.system().lower() == "linux":
    DEFAULT_TASK_KILL_LIST = ["avconv", "firefox", "chrome"]
    DEFAULT_TASK_KILL_CMD = "pkill "
    DEFAULT_EDITOR_CMD = "cat "
elif platform.system().lower() == "windows":
    DEFAULT_TASK_KILL_CMD = "taskkill /f /t /im "
    DEFAULT_TASK_KILL_LIST = ["ffmpeg", "firefox.exe", "chrome.exe"]
    DEFAULT_EDITOR_CMD = "type "
else:
    DEFAULT_TASK_KILL_LIST = ["ffmpeg", "firefox", "chrome"]
    DEFAULT_TASK_KILL_CMD = "pkill "
    DEFAULT_EDITOR_CMD = "open -e "


class RunTest(object):
    def __init__(self, **kwargs):
        self.logger = get_logger(__file__, kwargs['advance'])
        for variable_name in kwargs.keys():
            self.logger.debug("Set variable name: %s with value: %s" % (variable_name, kwargs[variable_name]))
            setattr(self, variable_name, kwargs[variable_name])

    def kill_legacy_process(self):
        for process_name in DEFAULT_TASK_KILL_LIST:
            cmd_str = DEFAULT_TASK_KILL_CMD + process_name
            os.system(cmd_str)

    def clean_up_output_data(self):
        # clean output folder
        output_dir = os.path.join(os.getcwd(), 'output')
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    def get_test_env(self, **kwargs):
        result = os.environ.copy()
        result['PROFILER'] = self.profiler
        result['KEEP_BROWSER'] = str(int(self.keep_browser))
        result['ENABLE_ONLINE'] = str(int(self.online))
        result['ONLINE_CONFIG'] = self.online_config
        result['ENABLE_ADVANCE'] = str(int(self.advance))
        result['CALC_SI'] = str(int(self.calc_si))
        result['ENABLE_WAVEFORM'] = str(int(self.waveform))
        if self.perfherder_revision:
            result['PERFHERDER_REVISION'] = self.perfherder_revision
        else:
            result['PERFHERDER_REVISION'] = ""
        if self.perfherder_pkg_platform:
            result['PERFHERDER_PKG_PLATFORM'] = self.perfherder_pkg_platform
        else:
            result['PERFHERDER_PKG_PLATFORM'] = ""
        for variable_name in kwargs.keys():
            result[variable_name] = str(kwargs[variable_name])
        return result

    def suite_content_parser(self, input_line):
        # in suite file, use comma to distinguish test case script, pre-execute script, post-execute script
        result = {}
        data_array = input_line.split(",")
        result[data_array[0]] = {}
        if len(data_array) == 3:
            if data_array[1].strip():
                result[data_array[0]]["PRE_SCRIPT_PATH"] = data_array[1].strip()
            if data_array[2].strip():
                result[data_array[0]]["POST_SCRIPT_PATH"] = data_array[2].strip()
        elif len(data_array) == 2:
            if data_array[1].strip():
                result[data_array[0]]["PRE_SCRIPT_PATH"] = data_array[1].strip()
        return result

    def create_exception_file(self, message, current_retry):
        if self.jenkins_build_no > 0:
            exception_status_dir = os.path.join(os.getcwd(), "agent_status")
            if os.path.exists(exception_status_dir) is False:
                os.mkdir(exception_status_dir)
            exception_status_file = os.path.join(exception_status_dir,
                                                 str(self.jenkins_build_no) + ".exception" + str(current_retry))
            with open(exception_status_file, "w") as write_fh:
                write_fh.write(message)

    def loop_test(self, test_case_module_name, test_name, test_env, current_run=0, current_retry=0):
        return_result = {"ip": None, "video_path": None, "test_name": None}
        while current_run < self.max_run:
            self.logger.info("The counter is %d and the retry counter is %d" % (current_run, current_retry))
            try:
                if self.online and os.path.exists(DEFAULT_RESULT_FP):
                    os.remove(DEFAULT_RESULT_FP)
                run_result = self.run_test(test_case_module_name, test_env)
                if run_result:
                    if "sikuli_stat" in run_result and int(run_result['sikuli_stat']) == 0 and "fps_stat" in run_result and int(run_result['fps_stat']) == 0:
                        if self.online:
                            # Online mode handling
                            upload_result = self.upload_agent_obj.upload_result(DEFAULT_RESULT_FP)
                            if upload_result:
                                self.logger.info("===== upload success =====")
                                self.logger.info(upload_result)
                                return_result['ip'] = upload_result['ip']
                                return_result['video_path'] = upload_result['video']
                                return_result['test_name'] = test_name
                                self.logger.info("===== upload success =====")
                                if "current_test_times" in upload_result:
                                    current_run = upload_result["current_test_times"]
                                    self.max_run = upload_result['config_test_times']
                                else:
                                    current_run += 1
                            else:

                                current_run += 1
                        else:
                            if "time_list_counter" in run_result:
                                current_run = int(run_result['time_list_counter'])
                            else:
                                current_run += 1
                    else:
                        current_retry += 1
                else:
                    current_retry += 1
            except Exception as e:
                print "Exception happend during running test!"
                print e.message
                self.create_exception_file(e.message, current_retry)
                current_retry += 1

            if current_retry >= self.max_retry:
                break
        return return_result

    def run_test(self, test_case_module_name, test_env):
        self.kill_legacy_process()

        self.logger.debug("========== Environment data ======")
        self.logger.debug(test_env)
        self.logger.debug("========== Environment data ======")
        self.logger.info(" ".join(["python", "-m", "unittest", test_case_module_name]))
        subprocess.call(["python", "-m", "unittest", test_case_module_name], env=test_env)

        if os.path.exists(DEFAULT_RUNNING_STAT_FN):
            with open(DEFAULT_RUNNING_STAT_FN) as stat_fh:
                stat_dict = json.load(stat_fh)
                return stat_dict
        else:
            self.logger.error("test could raise exception during execution!!")
            return None

    def loop_suite(self, type, input_suite_fp):
        with open(input_suite_fp) as input_suite_fh:
            for tmp_line in input_suite_fh.read().splitlines():
                if tmp_line:
                    case_data = self.suite_content_parser(tmp_line)
                    self.logger.info("======= case_data  ========")
                    self.logger.info(case_data)
                    self.logger.info("======= case_data  ========")
                    test_case = case_data.keys()[0]
                    case_data[test_case]["MAX_RUN"] = self.max_run

                    test_case_module_name = ""
                    if type == "pt":
                        test_case_module_name = DEFAULT_TEST_FOLDER + "." + "test_pilot_run"
                        case_data[test_case]["SIKULI_SCRIPT_PATH"] = test_case
                        case_data[test_case]["TEST_SCRIPT_PY_DIR_PATH"] = os.sep.join(test_case_module_name.split(".")[:-1])
                        test_env = self.get_test_env(**case_data[test_case])
                        if test_case.endswith(os.sep):
                            test_name = test_case.split(os.sep)[-2].split(".")[0]
                        else:
                            test_name = test_case.split(os.sep)[-1].split(".")[0]
                    else:
                        test_case_fp = test_case.replace(".", os.sep) + ".py"
                        test_name = test_case.split(".")[-1]
                        case_data[test_case]["TEST_SCRIPT_PY_DIR_PATH"] = os.sep.join(test_case.split(".")[:-1])
                        if os.path.exists(test_case_fp):
                            test_case_module_name = test_case
                            test_env = self.get_test_env(**case_data[test_case])
                        else:
                            self.logger.error("Test script [%s] is not exist!" % test_case_fp)
                            test_env = None
                    if self.online:
                        if self.perfherder_revision:
                            self.upload_agent_obj.upload_register_data(input_suite_fp, type)
                        self.upload_agent_obj.upload_videos(self.loop_test(test_case_module_name, test_name, test_env))
                    else:
                        self.loop_test(test_case_module_name, test_name, test_env)

            if self.online:
                self.clean_up_output_data()

    def run(self, type, input_suite_fp):
        if self.online:
            self.upload_agent_obj = UploadAgent(svr_config_fp=self.online_config, test_comment=self.test_comment)
        self.loop_suite(type, input_suite_fp)
        os.system(DEFAULT_EDITOR_CMD + " end.txt")


def main():
    start_time = time.time()
    arguments = docopt(__doc__)
    run_test_obj = RunTest(profiler=arguments['--profiler'], keep_browser=arguments['--keep-browser'],
                           max_run=int(arguments['--max-run']),
                           max_retry=int(arguments['--max-retry']), online=arguments['--online'],
                           online_config=arguments['--online-config'], advance=arguments['--advance'],
                           test_comment=arguments['--comment'], calc_si=arguments['--calc-si'],
                           waveform=arguments['--waveform'], perfherder_revision=arguments['--perfherder-revision'],
                           perfherder_pkg_platform=arguments['--perfherder-pkg-platform'], jenkins_build_no=arguments['--jenkins-build-no'])
    if arguments['pt']:
        run_test_obj.run("pt", arguments['<suite.txt>'])
    elif arguments['re']:
        run_test_obj.run("re", arguments['<suite.txt>'])
    else:
        run_test_obj.run("re", arguments['<suite.txt>'])
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger = get_logger(__file__, arguments['--advance'])
    logger.debug("Total Execution Time: [%s]" % elapsed_time)

if __name__ == '__main__':
    main()
