import os
import time
import json
import unittest
import helper.desktopHelper as desktopHelper
import helper.resultHelper as resultHelper
import lib.helper.targetHelper as targetHelper
import lib.sikuli as sikuli
import lib.helper.captureHelper as captureHelper
from common.environment import Environment
from helper.profilerHelper import Profilers


class PerfBaseTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(PerfBaseTest, self).__init__(*args, **kwargs)

        # Init environment variables
        self.env = Environment(self._testMethodName, self._testMethodDoc)

    def get_profiler_list(self):
        avconv_profiler = {"path": "lib.profiler.avconvProfiler", "name": "AvconvProfiler", "profile_name": None}
        har_profiler = {"path": "lib.profiler.harProfiler", "name": "HarProfiler", "profile_name": "AutoSaveHAR.zip"}
        performance_timing_profiler = {"path": "lib.profiler.performanceTimingProfiler",
                                       "name": "PerformanceTimingProfiler", "profile_name": None}
        gecko_profiler = {"path": "lib.profiler.geckoProfiler", "name": "GeckoProfiler",
                          "profile_name": "GeckoProfiler.zip"}
        result_list = []

        profiler_list_str = os.getenv("PROFILER")
        self.enabled_profiler_list = [item.strip() for item in profiler_list_str.split(',')]
        if self.env.PROFILER_FLAG_FXALL in self.enabled_profiler_list:
            result_list.append(avconv_profiler)
            result_list.append(har_profiler)
            result_list.append(performance_timing_profiler)
            result_list.append(gecko_profiler)
            return result_list

        if self.env.PROFILER_FLAG_JUSTPROFILER in self.enabled_profiler_list:
            result_list.append(har_profiler)
            result_list.append(performance_timing_profiler)
            result_list.append(gecko_profiler)
            return result_list

        if self.env.PROFILER_FLAG_AVCONV in self.enabled_profiler_list:
            result_list.append(avconv_profiler)

        if self.env.PROFILER_FLAG_GECKOPROFILER in self.enabled_profiler_list:
            result_list.append(gecko_profiler)

        if self.env.PROFILER_FLAG_HAREXPORT in self.enabled_profiler_list:
            result_list.append(har_profiler)

        return result_list

    def set_variable(self, **kwargs):
        for variable_name in kwargs.keys():
            setattr(self,variable_name,kwargs[variable_name])

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
        self.exec_timestamp_list.append(time.time())

        # minimize all windows
        desktopHelper.minimize_window()

        # launch browser
        if self.env.PROFILER_FLAG_CHROMETRACING in self.enabled_profiler_list:
            self.profile_dir_path = desktopHelper.launch_browser(self.browser_type, profile_path=self.profile_zip_path,
                                                                 tracing_path=self.env.chrome_tracing_file_fp)
        else:
            self.profile_dir_path = desktopHelper.launch_browser(self.browser_type, profile_path=self.profile_zip_path)

        # switch to content window, prevent cursor twinkling
        time.sleep(3)
        if self.browser_type == desktopHelper.DEFAULT_BROWSER_TYPE_FIREFOX:
            self.sikuli.run_test("test_firefox_switchcontentwindow", self.env.output_name)
        else:
            self.sikuli.run_test("test_chrome_switchcontentwindow", self.env.output_name)

        # lock browser start pos at (0,0)
        desktopHelper.lock_window_pos(self.browser_type)

        # execute pre-run-script.
        # You have to specify the pre_run_script and test_url before calling parent setup in your test class
        if hasattr(self, "pre_run_script"):
            # clone pre run script test url id
            if hasattr(self, "pre_run_script_test_url_id"):
                test_url_id = getattr(self.env, self.pre_run_script_test_url_id)
                self.test_url, self.test_url_id = self.target_helper.clone_target(test_url_id,
                                                                                  self.pre_run_script + "_" + self.env.time_stamp)
            # execute pre run script
            self.sikuli_status = self.sikuli.run_test( self.pre_run_script,
                                                 self.pre_run_script + "_" + self.env.time_stamp,
                                                 test_url=self.test_url)


        # clone test target
        if hasattr(self, "test_target"):
            self.test_url, self.test_url_id = self.target_helper.clone_target(self.test_target, self.env.output_name)

        # capture 1st snapshot
        time.sleep(5)

        if self.env.PROFILER_FLAG_AVCONV in self.enabled_profiler_list or self.env.PROFILER_FLAG_FXALL in self.enabled_profiler_list:
            captureHelper.capture_screen(self.env, self.env.video_output_sample_1_fp, self.env.img_sample_dp,
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
            captureHelper.capture_screen(self.env, self.env.video_output_sample_2_fp, self.env.img_sample_dp,
                                         self.env.img_output_sample_2_fn)

        # Stop profiler and save profile data
        self.profilers.stop_profiling(self.profile_dir_path)

        # Post run sikuli script
        if os.getenv("POST_SCRIPT_PATH"):
            self.sikuli.run_sikulix_cmd(os.getenv("POST_SCRIPT_PATH"))

        # Stop browser
        if int(os.getenv("KEEP_BROWSER")) == 0:
            self.sikuli.close_browser(self.browser_type)

        # Delete Url
        if hasattr(self,"test_url_id"):
            self.target_helper.delete_target(self.test_url_id)

        # output sikuli status to static file
        with open(self.env.DEFAULT_STAT_RESULT, "w") as fh:
            stat_data = {'sikuli_stat' : str(self.sikuli_status)}
            json.dump(stat_data,fh)

        # output result
        if self.sikuli_status == 0:
            if hasattr(self, "crop_data"):
                resultHelper.result_calculation(self.env, self.exec_timestamp_list, self.crop_data)
            else:
                resultHelper.result_calculation(self.env,  self.exec_timestamp_list)
        else:
            print "[WARNING] This running result of sikuli execution is not successful, return code: " + str(self.sikuli_status)
