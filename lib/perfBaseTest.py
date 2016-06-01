import os
import time
import unittest
import helper.desktopHelper as desktopHelper
import helper.resultHelper as resultHelper
import lib.helper.targetHelper as targetHelper
import lib.sikuli as sikuli
import lib.helper.captureHelper as captureHelper
from common.environment import Environment
from helper.profilerHelper import Profilers


class PerfBaseTest(unittest.TestCase):

    def get_profiler_list(self):
        avconv_profiler = {"path": "lib.profiler.avconvProfiler", "name": "AvconvProfiler", "profile_name": None}
        har_profiler = {"path": "lib.profiler.harProfiler", "name": "HarProfiler", "profile_name": "AutoSaveHAR.zip"}
        performance_timing_profiler = {"path": "lib.profiler.performanceTimingProfiler", "name": "PerformanceTimingProfiler", "profile_name": None}
        gecko_profiler = {"path": "lib.profiler.geckoProfiler", "name": "GeckoProfiler", "profile_name": "GeckoProfiler.zip"}
        result_list = []
        if int(os.getenv("ENABLE_PROFILER")) == 1:
            if int(os.getenv("DISABLE_AVCONV")) == 0:
                result_list.append(avconv_profiler)
            result_list.append(har_profiler)
            result_list.append(performance_timing_profiler)
            result_list.append(gecko_profiler)
        else:
            result_list.append(avconv_profiler)
        return result_list

    def setUp(self):

        # Get profiler list
        self.profiler_list = self.get_profiler_list()

        # Init environment variables
        self.env = Environment(self._testMethodName, self._testMethodDoc)

        # Init output dirs
        self.env.init_output_dir()

        # Init sikuli status
        self.sikuli_status = 0

        # get browser type
        self.browser_type = self.env.get_browser_type()

        # init target helper
        self.target_helper = targetHelper.TagetHelper(self.env)

        # init sikuli
        self.sikuli = sikuli.Sikuli()

        # Start video recordings
        self.profilers = Profilers(self.env, self.browser_type, self.sikuli)
        self.profilers.start_profiling(self.profiler_list)
        self.profile_zip_path = self.profilers.get_profile_path()

        # minimize all windows
        desktopHelper.minimize_window()

        # launch browser
        self.profile_dir_path = desktopHelper.launch_browser(self.browser_type, self.profile_zip_path)

        # switch to content window, prevent cursor twinkling
        time.sleep(3)
        if self.browser_type == desktopHelper.DEFAULT_BROWSER_TYPE_FIREFOX:
            self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, "test_firefox_switchcontentwindow",
                            self.env.test_method_name + "_" + self.env.time_stamp)
        else:
            self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, "test_chrome_switchcontentwindow",
                            self.env.test_method_name + "_" + self.env.time_stamp)

        # execute pre-run-script.
        # You have to specify the pre_run_script and test_url before calling parent setup in your test class
        if hasattr(self, "pre_run_script"):
            # clone pre run script test url id
            if hasattr(self, "pre_run_script_test_url_id"):
                test_url_id = getattr(self.env, self.pre_run_script_test_url_id)
                self.test_url, self.test_url_id = self.target_helper.clone_target(test_url_id,
                                                                                  self.pre_run_script + "_" + self.env.time_stamp)
            # execute pre run script
            self.sikuli_status = self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, self.pre_run_script,
                                                 self.pre_run_script + "_" + self.env.time_stamp,
                                                 test_url=self.test_url)

        # capture 1st snapshot
        time.sleep(5)
        captureHelper.capture_screen(self.env, self.env.video_output_sample_1_fp, self.env.img_sample_dp,
                                     self.env.img_output_sample_1_fn)

    def tearDown(self):

        # capture 2nd snapshot
        time.sleep(5)
        captureHelper.capture_screen(self.env, self.env.video_output_sample_2_fp, self.env.img_sample_dp,
                                     self.env.img_output_sample_2_fn)

        # Stop profiler and save profile data
        self.profilers.stop_profiling(self.profile_dir_path)

        # Stop browser
        if int(os.getenv("CLOSE_BROWSER")) == 1:
            desktopHelper.stop_browser(self.browser_type, self.env)

        # Delete Url
        if self.test_url_id:
            self.target_helper.delete_target(self.test_url_id)

        # output sikuli status to static file
        with open(self.env.DEFAULT_SIKULI_STATUS_RESULT, "w") as fh:
            fh.write(str(self.sikuli_status))

        # output result
        if self.sikuli_status == 0:
            resultHelper.result_calculation(self.env)
        else:
            print "[WARNING] This running result of sikuli execution is not successful, return code: " + str(self.sikuli_status)
