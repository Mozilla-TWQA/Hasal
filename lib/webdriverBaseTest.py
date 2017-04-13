import json
import time
import baseTest
import lib.webdriver as wd
import helper.desktopHelper as desktopHelper
import lib.helper.videoHelper as videoHelper
from helper.profilerHelper import Profilers
from common.logConfig import get_logger

logger = get_logger(__name__)


class WebdriverBaseTest(baseTest.BaseTest):

    def __init__(self, *args, **kwargs):
        super(WebdriverBaseTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(WebdriverBaseTest, self).setUp()

        # launch browser
        self.browser_obj, self.profile_dir_path = \
            desktopHelper.launch_browser(self.browser_type, env=self.env, type='webdriver',
                                         profiler_list=self.env.firefox_settings_extensions)
        self.driver = self.browser_obj.return_driver()
        self.wd = wd.Webdriver(self.driver)

        # Start video recordings
        # TODO: need to be webdriver related / geckoProfiler and performanceTimingProfiler used Sikuli object
        self.profilers = Profilers(self.env, self.browser_type, self.wd)
        self.profilers.start_profiling(self.env.firefox_settings_extensions)

        # Record initial timestamp
        with open(self.env.DEFAULT_TIMESTAMP, "w") as fh:
            timestamp = {self.env.INITIAL_TIMESTAMP_NAME: str(time.time())}
            json.dump(timestamp, fh)

        # wait browser ready / must do after launching browser and starting of video recording
        self.get_browser_done()

        # capture 1st snapshot
        time.sleep(5)
        if self.index_config['snapshot-base-sample1']:
            videoHelper.capture_screen(self.env, self.index_config, self.env.video_output_sample_1_fp, self.env.img_sample_dp,
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
        if self.index_config['snapshot-base-sample2']:
            videoHelper.capture_screen(self.env, self.index_config, self.env.video_output_sample_2_fp, self.env.img_sample_dp,
                                       self.env.img_output_sample_2_fn)

        # Stop profiler and save profile data
        self.profilers.stop_profiling(self.profile_dir_path)

        # Stop browser
        if self.exec_config['keep-browser'] is False:
            self.wd.close_browser(self.browser_type)

        super(WebdriverBaseTest, self).tearDown()
