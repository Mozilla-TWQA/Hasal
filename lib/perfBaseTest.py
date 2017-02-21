import os
import time
import baseTest
import helper.desktopHelper as desktopHelper
import lib.sikuli as sikuli
import lib.helper.videoHelper as videoHelper
from helper.profilerHelper import Profilers
from common.logConfig import get_logger

logger = get_logger(__name__)


class PerfBaseTest(baseTest.BaseTest):

    def __init__(self, *args, **kwargs):
        super(PerfBaseTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(PerfBaseTest, self).setUp()

        # init sikuli
        self.sikuli = sikuli.Sikuli(self.env.run_sikulix_cmd_path, self.env.hasal_dir)

        # Start video recordings
        self.profilers = Profilers(self.env, self.browser_type, self.sikuli)
        self.profilers.start_profiling(self.env.firefox_settings_extensions)

        # Record timestamp t1
        self.exec_timestamp_list.append(self.profilers.get_t1_time())

        # minimize all windows
        desktopHelper.minimize_window()

        # launch browser
        self.profile_dir_path = desktopHelper.launch_browser(self.browser_type, env=self.env,
                                                             profiler_list=self.env.firefox_settings_extensions)

        # wait browser ready
        self.get_browser_done()

        # execute pre-run-script.
        # You have to specify the pre_run_script and test_url before calling parent setup in your test class
        if os.getenv("PRE_SCRIPT_PATH"):
            pre_script_args = []

            # clone pre run script test url id
            if hasattr(self, "pre_script_args"):
                pre_script_args = self.args_parser(os.getenv("PRE_SCRIPT_PATH"), self.pre_script_args)

            # execute pre run script
            self.round_status = self.sikuli.run_test(os.getenv("PRE_SCRIPT_PATH"),
                                                      os.getenv("PRE_SCRIPT_PATH") + "_" + self.env.time_stamp,
                                                      args_list=pre_script_args)

        # capture 1st snapshot
        time.sleep(5)

        if self.env.PROFILER_FLAG_AVCONV in self.env.firefox_settings_extensions:
            if self.env.firefox_settings_extensions[self.env.PROFILER_FLAG_AVCONV]['enable'] is True:
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

        if self.env.PROFILER_FLAG_AVCONV in self.env.firefox_settings_extensions:
            if self.env.firefox_settings_extensions[self.env.PROFILER_FLAG_AVCONV]['enable'] is True:
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

        super(PerfBaseTest, self).tearDown()
