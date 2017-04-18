import time
import json
import baseTest
import helper.desktopHelper as desktopHelper
import lib.sikuli as sikuli
import lib.helper.videoHelper as videoHelper
from helper.profilerHelper import Profilers
from common.logConfig import get_logger
from common.commonUtil import CommonUtil

logger = get_logger(__name__)


class PerfBaseTest(baseTest.BaseTest):

    def __init__(self, *args, **kwargs):
        super(PerfBaseTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(PerfBaseTest, self).setUp()

        # init sikuli
        self.sikuli = sikuli.Sikuli(self.env.run_sikulix_cmd_path, self.env.hasal_dir)

        # Start video recordings
        self.profilers = Profilers(self.env, self.index_config, self.browser_type, self.sikuli)
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

        # capture 1st snapshot
        time.sleep(5)

        # check the video recording
        recording_enabled = CommonUtil.is_video_recording(self.firefox_config)
        if recording_enabled and self.index_config.get('snapshot-base-sample1', False) is True:
            videoHelper.capture_screen(self.env, self.index_config, self.env.video_output_sample_1_fp,
                                       self.env.img_sample_dp,
                                       self.env.img_output_sample_1_fn)
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

        if self.env.PROFILER_FLAG_AVCONV in self.env.firefox_settings_extensions:
            if self.env.firefox_settings_extensions[self.env.PROFILER_FLAG_AVCONV]['enable'] is True and self.index_config['snapshot-base-sample2'] is True:
                videoHelper.capture_screen(self.env, self.index_config, self.env.video_output_sample_2_fp, self.env.img_sample_dp,
                                           self.env.img_output_sample_2_fn)

        # Stop profiler and save profile data
        self.profilers.stop_profiling(self.profile_dir_path)

        # Stop browser
        if self.exec_config['keep-browser'] is False:
            desktopHelper.close_browser(self.browser_type)

        super(PerfBaseTest, self).tearDown()
