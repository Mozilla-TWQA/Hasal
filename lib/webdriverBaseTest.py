import os
import time
import baseTest
import lib.webdriver as webdriver
import helper.desktopHelper as desktopHelper
import lib.helper.videoHelper as videoHelper
from helper.profilerHelper import Profilers
from common.logConfig import get_logger

logger = get_logger(__name__)


class WebdriverBaseTest(baseTest.BaseTest):

    def __init__(self, *args, **kwargs):
        super(WebdriverBaseTest, self).__init__(*args, **kwargs)
        self.browser = None

    def setUp(self):
        super(WebdriverBaseTest, self).setUp()

        # TODO: init webdriver / way to stop browser
        self.webdriver = webdriver.Webdriver(self.env.run_sikulix_cmd_path, self.env.hasal_dir)

        # Start video recordings
        # TODO: need to be webdriver related / geckoProfiler and performanceTimingProfiler used Sikuli object
        self.profilers = Profilers(self.env, self.browser_type, self.sikuli)
        self.profilers.start_profiling(self.env.firefox_settings_extensions)

        # Record timestamp t1
        self.exec_timestamp_list.append(self.profilers.get_t1_time())

        # minimize all windows
        desktopHelper.minimize_window()

        # launch browser
        # TODO: should modify webdriverChrome and webdriverFirefox
        self.browser = desktopHelper.launch_browser(self.browser_type, env=self.env, type='webdriver',
                                                    profiler_list=self.env.firefox_settings_extensions)

        # wait browser ready
        self.get_browser_done()

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

        # Stop browser
        if int(os.getenv("KEEP_BROWSER")) == 0:
            self.webdriver.close_browser(self.browser_type)

        super(WebdriverBaseTest, self).tearDown()
