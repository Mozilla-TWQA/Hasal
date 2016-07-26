"""runtest.

Usage:
  runtest.py regression <suite.txt> [--online] [--online-config=<str>] [--max-run=<int>] [--max-retry=<int>] [--keep-browser=<int>] [--profiler=<str>]
  runtest.py pilottest <suite.txt> [--max-run=<int>] [--max-retry=<int>] [--keep-browser=<int>] [--profiler=<str>]
  runtest.py (-h | --help)

Options:
  -h --help                 Show this screen.
  --max-run=<int>           Test run max no [default: 40].
  --max-retry=<int>         Test failed retry max no [default: 15].
  --keep-browser=<int>      Keep the browser open after test script executed [default: 0]
  --profiler=<str>          Enabled profiler, current support profiler:avconv,geckoprofiler,harexport,chrometracing,fxall,justprofiler [default: avconv]
  --online                  Result will be transfer to server, calculated by server
  --online-config=<str>     Online server config [default: server.json]


"""
import os
import json
import platform
import subprocess
from docopt import docopt

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
        for variable_name in kwargs.keys():
            print "Set variable name: %s with value: %s" % (variable_name, kwargs[variable_name])
            setattr(self, variable_name, kwargs[variable_name])

    def kill_legacy_process(self):
        for process_name in DEFAULT_TASK_KILL_LIST:
            cmd_str = DEFAULT_TASK_KILL_CMD + process_name
            os.system(cmd_str)

    def get_test_env(self, **kwargs):
        result = os.environ.copy()
        result['PROFILER'] = self.profiler
        result['KEEP_BROWSER'] = str(self.keep_browser)
        result['ENABLE_ONLINE'] = str(self.online)
        result['ONLINE_CONFIG'] = self.online_config
        for variable_name in kwargs.keys():
            result[variable_name] = str(kwargs[variable_name])
        return result

    def suite_content_parser(self, input_line):
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

    def loop_test(self, test_case_module_name, test_env, current_run=0, current_retry=0):
        while current_run < self.max_run:
            print "The counter is %d and the retry counter is %d" % (current_run, current_retry)
            run_result = self.run_test(test_case_module_name, test_env)
            if run_result:
                if "sikuli_stat" in run_result and int(run_result['sikuli_stat']) == 0:
                    if "time_list_counter" in run_result:
                        current_run = int(run_result['time_list_counter'])
                    else:
                        current_run += 1
                else:
                    current_retry += 1
            else:
                current_retry += 1
            if current_retry >= self.max_retry:
                break

    def run_test(self, test_case_module_name, test_env):
        self.kill_legacy_process()

        print "========== Environment data ======"
        print test_env
        print "========== Environment data ======"
        print " ".join(["python", "-m", "unittest", test_case_module_name])
        subprocess.call(["python", "-m", "unittest", test_case_module_name], env=test_env)

        if os.path.exists(DEFAULT_RUNNING_STAT_FN):
            with open(DEFAULT_RUNNING_STAT_FN) as stat_fh:
                stat_dict = json.load(stat_fh)
                return stat_dict
        else:
            print "[ERROR] test could raise exception during execution!!"
            return None

    def regression_loop_suite(self, input_suite_fp):
        with open(input_suite_fp) as input_suite_fh:
            for tmp_line in input_suite_fh.read().splitlines():
                case_data = self.suite_content_parser(tmp_line)
                test_case_name = case_data.keys()[0]
                test_case_fp = os.path.join(os.getcwd(), DEFAULT_TEST_FOLDER, test_case_name + ".py")
                if os.path.exists(test_case_fp):
                    test_case_module_name = DEFAULT_TEST_FOLDER + "." + test_case_name
                    test_env = self.get_test_env(**case_data[test_case_name])
                    self.loop_test(test_case_module_name, test_env)

    def pilottest_loop_suite(self, input_suite_fp):
        with open(input_suite_fp) as input_suite_fh:
            for tmp_line in input_suite_fh.read().splitlines():
                test_case_module_name = DEFAULT_TEST_FOLDER + "." + "test_pilot_run"
                case_data = self.suite_content_parser(tmp_line)
                test_sikuli_fp = case_data.keys()[0]
                case_data[test_sikuli_fp]["SIKULI_SCRIPT_PATH"] = test_sikuli_fp
                test_env = self.get_test_env(**case_data[test_sikuli_fp])
                self.loop_test(test_case_module_name, test_env)

    def run(self, type, input_suite_fp):
        if type == "pilottest":
            self.pilottest_loop_suite(input_suite_fp)
        else:
            self.regression_loop_suite(input_suite_fp)
        os.system(DEFAULT_EDITOR_CMD + " end.txt")


def main():
    arguments = docopt(__doc__)
    print arguments
    run_test_obj = RunTest(profiler=arguments['--profiler'], keep_browser=arguments['--keep-browser'],
                           max_run=int(arguments['--max-run']),
                           max_retry=int(arguments['--max-retry']), online=arguments['--online'],
                           online_config=arguments['--online-config'])
    if arguments['pilottest']:
        run_test_obj.run("pilottest", arguments['<suite.txt>'])
    elif arguments['regression']:
        run_test_obj.run("regression", arguments['<suite.txt>'])
    else:
        run_test_obj.run("regression", arguments['<suite.txt>'])

if __name__ == '__main__':
    main()
