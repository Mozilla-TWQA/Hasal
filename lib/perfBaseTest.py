import os
import time
import json
import baseTest
import helper.desktopHelper as desktopHelper
import lib.sikuli as sikuli
import lib.helper.videoHelper as videoHelper
from helper.profilerHelper import Profilers
from lib.common.visualmetricsWrapper import find_image_viewport
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

        # Record initial timestamp
        with open(self.env.DEFAULT_TIMESTAMP, "w") as fh:
            timestamp = {self.env.INITIAL_TIMESTAMP_NAME: str(time.time())}
            json.dump(timestamp, fh)

        # launch browser
        _, self.profile_dir_path = desktopHelper.launch_browser(self.browser_type, env=self.env,
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
        if int(os.getenv("ENABLE_WAVEFORM")) == 3:
            start_fp = os.path.join(self.env.img_sample_dp, self.env.img_output_sample_1_fn)
            self.viewport = find_image_viewport(start_fp)
        time.sleep(2)

        # Record timestamp t1
        with open(self.env.DEFAULT_TIMESTAMP, "r+") as fh:
            timestamp = json.load(fh)
            timestamp['t1'] = time.time()
            fh.seek(0)
            fh.write(json.dumps(timestamp))

    def tearDown(self):

        # Record timestamp t2
        with open(self.env.DEFAULT_TIMESTAMP, "r+") as fh:
            timestamp = json.load(fh)
            if 't2' not in timestamp:
                timestamp['t2'] = time.time()
                fh.seek(0)
                fh.write(json.dumps(timestamp))

        # capture 2nd snapshot
        time.sleep(5)

        if not int(os.getenv("ENABLE_WAVEFORM")) and self.env.PROFILER_FLAG_AVCONV in self.env.firefox_settings_extensions:
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
