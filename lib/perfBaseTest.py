import os
import time
import json
import unittest
import helper.desktopHelper as desktopHelper
import helper.resultHelper as resultHelper
import lib.helper.targetHelper as targetHelper
import lib.sikuli as sikuli
import lib.helper.videoHelper as videoHelper
from common.environment import Environment
from helper.profilerHelper import Profilers
from common.logConfig import get_logger

logger = get_logger(__name__)


class PerfBaseTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(PerfBaseTest, self).__init__(*args, **kwargs)

        # Init environment variables
        self.env = Environment(self._testMethodName, self._testMethodDoc)

    def get_profiler_list(self):
        avconv_profiler = {"path": "lib.profiler.avconvProfiler", "name": "AvconvProfiler", "profile_name": None}
        mitmdump_profiler = {"path": "lib.profiler.mitmDumpProfiler", "name": "MitmDumpProfiler", "profile_name": None}
        har_profiler = {"path": "lib.profiler.harProfiler", "name": "HarProfiler", "profile_name": "AutoSaveHAR.zip"}
        performance_timing_profiler = {"path": "lib.profiler.performanceTimingProfiler",
                                       "name": "PerformanceTimingProfiler", "profile_name": None}
        gecko_profiler = {"path": "lib.profiler.geckoProfiler", "name": "GeckoProfiler",
                          "profile_name": "GeckoProfiler.zip"}
        tracelogger_profiler = {"path": "lib.profiler.traceloggerProfiler", "name": "TraceLoggerProfiler",
                                "profile_name": None}
        result_list = []

        profiler_list_str = os.getenv("PROFILER")
        self.enabled_profiler_list = [item.strip() for item in profiler_list_str.split(',')]
        if self.env.PROFILER_FLAG_FXALL in self.enabled_profiler_list:
            result_list.append(avconv_profiler)
            result_list.append(har_profiler)
            result_list.append(performance_timing_profiler)
            result_list.append(gecko_profiler)
            result_list.append(tracelogger_profiler)
            return result_list

        if self.env.PROFILER_FLAG_JUSTPROFILER in self.enabled_profiler_list:
            result_list.append(har_profiler)
            result_list.append(performance_timing_profiler)
            result_list.append(gecko_profiler)
            result_list.append(tracelogger_profiler)
            return result_list

        if self.env.PROFILER_FLAG_AVCONV in self.enabled_profiler_list:
            result_list.append(avconv_profiler)

        if self.env.PROFILER_FLAG_GECKOPROFILER in self.enabled_profiler_list:
            result_list.append(performance_timing_profiler)
            result_list.append(gecko_profiler)

        if self.env.PROFILER_FLAG_HAREXPORT in self.enabled_profiler_list:
            result_list.append(har_profiler)

        if self.env.PROFILER_FLAG_MITMDUMP in self.enabled_profiler_list:
            result_list.append(mitmdump_profiler)

        if self.env.PROFILER_FLAG_FXTRACELOGGER in self.enabled_profiler_list:
            result_list.append(tracelogger_profiler)

        return result_list

    def set_variable(self, **kwargs):
        for variable_name in kwargs.keys():
            setattr(self, variable_name, kwargs[variable_name])

    def args_parser(self, input_script_name, input_args):
        result_args = []
        for arg in input_args:
            if type(arg) == dict:
                if "clone_url" in arg.keys():
                    test_url_id = getattr(self.env, arg["clone_url"])
                    self.test_url, self.test_url_id = self.target_helper.clone_target(test_url_id, input_script_name + "_" + self.env.time_stamp)
                    result_args.append(arg["clone_url"])
                else:
                    result_args.append(arg[arg.keys()[0]])
            else:
                result_args = input_args
        return result_args

    def setUp(self):

        # Get profiler list
        self.profiler_list = self.get_profiler_list()

        # Init output dirs
        self.env.init_output_dir()

        # Init sikuli status
        self.sikuli_status = 0

        # Init timestamp list
        self.exec_timestamp_list = []

        # get browser type
        self.browser_type = self.env.get_browser_type()

        # init target helper
        self.target_helper = targetHelper.TagetHelper(self.env)

        # init sikuli
        self.sikuli = sikuli.Sikuli(self.env.run_sikulix_cmd_path, self.env.hasal_dir)

        # Start video recordings
        self.profilers = Profilers(self.env, self.browser_type, self.sikuli)
        self.profilers.start_profiling(self.profiler_list)
        self.profile_zip_path = self.profilers.get_profile_path()

        # Record timestamp t1
        self.exec_timestamp_list.append(self.profilers.get_t1_time())

        # minimize all windows
        desktopHelper.minimize_window()

        # launch browser
        self.profile_dir_path = desktopHelper.launch_browser(self.browser_type, profile_path=self.profile_zip_path,
                                                             env=self.env,
                                                             enabled_profiler_list=self.enabled_profiler_list)

        # lock browser start pos at (0,0)
        desktopHelper.lock_window_pos(self.browser_type)
        if self.env.PROFILER_FLAG_AVCONV in self.enabled_profiler_list or self.env.PROFILER_FLAG_FXALL in self.enabled_profiler_list:
            videoHelper.capture_screen(self.env, self.env.video_output_sample_1_fp, self.env.img_sample_dp,
                                       self.env.img_output_sample_1_fn)
        desktopHelper.adjust_viewport(self.browser_type, self.env.img_sample_dp, self.env.img_output_sample_1_fn)

        # execute pre-run-script.
        # You have to specify the pre_run_script and test_url before calling parent setup in your test class
        if os.getenv("PRE_SCRIPT_PATH"):
            pre_script_args = []

            # clone pre run script test url id
            if hasattr(self, "pre_script_args"):
                pre_script_args = self.args_parser(os.getenv("PRE_SCRIPT_PATH"), self.pre_script_args)

            # execute pre run script
            self.sikuli_status = self.sikuli.run_test(os.getenv("PRE_SCRIPT_PATH"),
                                                      os.getenv("PRE_SCRIPT_PATH") + "_" + self.env.time_stamp,
                                                      args_list=pre_script_args)

        # clone test target
        if hasattr(self, "test_target"):
            if hasattr(self, "target_folder"):
                self.test_url, self.test_url_id = self.target_helper.clone_target(self.test_target,
                                                                                  self.env.output_name,
                                                                                  self.target_folder)
                logger.info("The test url after cloned is : [%s]" % self.test_url)
            else:
                self.test_url, self.test_url_id = self.target_helper.clone_target(self.test_target,
                                                                                  self.env.output_name)
                logger.info("The test url after cloned is : [%s]" % self.test_url)

        # capture 1st snapshot
        time.sleep(5)

        if self.env.PROFILER_FLAG_AVCONV in self.enabled_profiler_list or self.env.PROFILER_FLAG_FXALL in self.enabled_profiler_list:
            videoHelper.capture_screen(self.env, self.env.video_output_sample_1_fp, self.env.img_sample_dp,
                                       self.env.img_output_sample_1_fn)
        time.sleep(2)

        # Record timestamp t2
        self.exec_timestamp_list.append(time.time())

    def tearDown(self):

        # Record timestamp t3
        self.exec_timestamp_list.append(time.time())

        # capture 2nd snapshot
        time.sleep(5)

        if self.env.PROFILER_FLAG_AVCONV in self.enabled_profiler_list or self.env.PROFILER_FLAG_FXALL in self.enabled_profiler_list:
            videoHelper.capture_screen(self.env, self.env.video_output_sample_2_fp, self.env.img_sample_dp,
                                       self.env.img_output_sample_2_fn)

        # Stop profiler and save profile data
        self.profilers.stop_profiling(self.profile_dir_path)

        # Post run sikuli script
        if os.getenv("POST_SCRIPT_PATH"):
            post_script_args = []
            if hasattr(self, "post_script_args"):
                post_script_args = self.args_parser(os.getenv("POST_SCRIPT_PATH"), self.post_script_args)
            self.sikuli.run_test(os.getenv("POST_SCRIPT_PATH"),
                                 os.getenv("POST_SCRIPT_PATH") + "_" + self.env.time_stamp, args_list=post_script_args)

        # Stop browser
        if int(os.getenv("KEEP_BROWSER")) == 0:
            self.sikuli.close_browser(self.browser_type)

        # Delete Url
        if hasattr(self, "test_url_id"):
            self.target_helper.delete_target(self.test_url_id)

        # output sikuli status to static file
        with open(self.env.DEFAULT_STAT_RESULT, "w") as fh:
            stat_data = {'sikuli_stat': str(self.sikuli_status)}
            json.dump(stat_data, fh)

        # output result
        if self.sikuli_status == 0:
            if hasattr(self, "crop_data"):
                resultHelper.result_calculation(self.env, self.exec_timestamp_list, self.crop_data,
                                                int(os.getenv("CALC_SI")), int(os.getenv("ENABLE_WAVEFORM")),
                                                os.getenv("PERFHERDER_REVISION"), os.getenv("PERFHERDER_PKG_PLATFORM"))
            else:
                resultHelper.result_calculation(self.env, self.exec_timestamp_list, calc_si=int(os.getenv("CALC_SI")),
                                                waveform=int(os.getenv("ENABLE_WAVEFORM")),
                                                revision=os.getenv("PERFHERDER_REVISION"),
                                                pkg_platform=os.getenv("PERFHERDER_PKG_PLATFORM"))
        else:
            logger.warning("This running result of sikuli execution is not successful, return code: " + str(self.sikuli_status))
