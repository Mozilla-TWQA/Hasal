__author__ = 'shako'
import os
import subprocess
import platform
import argparse
from argparse import ArgumentDefaultsHelpFormatter

DEFAULT_TEST_FOLDER = "tests"
DEFAULT_MAX_RUN = 40
DEFAULT_MAX_RETRY = 15
DEFAULT_SIKULI_STAT_FN = "sikuli_stat.txt"
DEFAULT_TIME_LIST_COUNTER_FN = "time_list_counter.txt"

if platform.system().lower() == "windows":
    DEFAULT_TASK_KILL_CMD = "taskkill /f /t /im "
else:
    DEFAULT_TASK_KILL_CMD = "pkill "

if platform.system().lower() == "linux":
    DEFAULT_TASK_KILL_LIST = ["avconv", "firefox", "chrome"]
    DEFAULT_EDITOR_CMD = "gedit "
elif platform.system().lower() == "windows":
    DEFAULT_TASK_KILL_LIST = ["ffmpeg", "firefox.exe", "chrome.exe"]
    DEFAULT_EDITOR_CMD = "notepad "
else:
    DEFAULT_TASK_KILL_LIST = ["ffmpeg", "firefox", "chrome"]
    DEFAULT_EDITOR_CMD = "/Applications/Notes.app/Contents/MacOS/Notes"

class RunTest(object):
    def __init__(self, enable_profiler, disable_avconv, close_browser):
        self.enable_profiler = enable_profiler
        self.disable_avconv = disable_avconv
        self.close_browser = close_browser

    def kill_legacy_process(self):
        for process_name in DEFAULT_TASK_KILL_LIST:
            cmd_str = DEFAULT_TASK_KILL_CMD + process_name
            os.system(cmd_str)


    def loop_suite(self, input_suite_fp, input_max_retry, input_max_run):
        with open(input_suite_fp) as input_suite_fh:
            for read_line in input_suite_fh.readlines():
                test_case_name = read_line.strip()
                test_case_fp = os.path.join(os.getcwd(), DEFAULT_TEST_FOLDER, test_case_name + ".py")
                if os.path.exists(test_case_fp):
                    test_case_module_name = DEFAULT_TEST_FOLDER + "." + test_case_name
                    test_env = os.environ.copy()
                    test_env['ENABLE_PROFILER'] = self.enable_profiler
                    test_env['DISABLE_AVCONV'] = self.disable_avconv
                    test_env['CLOSE_BROWSER'] = self.close_browser
                    current_run = 0
                    current_retry = 0
                    while current_run < input_max_run:
                        self.kill_legacy_process()
                        print "The counter is %d and the retry_counter is %d" % (current_run, current_retry)
                        subprocess.call(["python", "-m", "unittest", test_case_module_name], env=test_env)
                        with open(DEFAULT_SIKULI_STAT_FN) as sikuli_stat_fh:
                            sikuli_stat = int(sikuli_stat_fh.read())
                            if sikuli_stat == 0:
                                with open(DEFAULT_TIME_LIST_COUNTER_FN) as time_list_counter_fh:
                                    current_run = int(time_list_counter_fh.read())
                            else:
                                current_retry+=1
                                if current_retry > input_max_retry:
                                    break
                else:
                    print "Test case[%s] not exist!" % test_case_fp

    def run(self, input_suite_fp, input_max_retry, input_max_run):
        self.loop_suite(input_suite_fp, input_max_retry, input_max_run)
        os.system(DEFAULT_EDITOR_CMD + " end.txt" )



def main():
    arg_parser = argparse.ArgumentParser(description='Run test suite script',
                                         formatter_class=ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('--enable_profiler', action='store_true', dest='enable_profiler_flag', default=False,
                            help='enable profiler', required=False)
    arg_parser.add_argument('--disable_avconv', action='store_true', dest='disable_avconv_flag', default=False,
                            help='disable avconv', required=False)
    arg_parser.add_argument('--keep_browser', action='store_false', dest='keep_browser_flag', default=True,
                            help='keep browser', required=False)
    arg_parser.add_argument('-i', action='store', dest='input_suite_fp', default=None,
                            help='specify suite file path', required=True)
    arg_parser.add_argument('--max_retry', action='store', dest='input_max_retry', default=DEFAULT_MAX_RETRY,
                            help='specify max retry count', required=False)
    arg_parser.add_argument('--max_run', action='store', dest='input_max_run', default=DEFAULT_MAX_RUN,
                            help='specify max retry run', required=False)
    args = arg_parser.parse_args()

    enable_profiler_flag = "0"
    disable_avconv_flag = "0"
    keep_browser_flag = "1"

    if args.enable_profiler_flag:
        enable_profiler_flag = "1"

    if args.disable_avconv_flag:
        disable_avconv_flag = "1"

    if args.keep_browser_flag:
        keep_browser_flag = "0"

    run_test_obj = RunTest(enable_profiler_flag, disable_avconv_flag, keep_browser_flag)

    if args.input_max_retry:
        input_max_retry = int(args.input_max_retry)
    if args.input_max_run:
        input_max_run = int(args.input_max_run)

    run_test_obj.run(args.input_suite_fp, input_max_retry, input_max_run)


if __name__ == '__main__':
    main()
