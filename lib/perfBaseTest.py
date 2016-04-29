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

    # profiler_list = [{"path": "lib.profiler.avconvProfiler", "name": "AvconvProfiler", "profile_name": None},
    #                  {"path": "lib.profiler.geckoProfiler", "name": "GeckoProfiler", "profile_name": "GeckoProfiler.zip"},
    #                  {"path": "lib.profiler.harProfiler", "name": "HarProfiler", "profile_name": "AutoSaveHAR.zip"}]
    profiler_list = [{"path": "lib.profiler.avconvProfiler", "name": "AvconvProfiler", "profile_name": None}]

    def setUp(self):
        # Init environment variables
        self.env = Environment(self._testMethodName)

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

        # trigger network console if needed
        desktopHelper.trigger_network_console(self.browser_type,self.sikuli,self.env, self.profiler_list)

        # switch to content window, prevent cursor twinkling
        time.sleep(3)
        if self.browser_type == desktopHelper.DEFAULT_BROWSER_TYPE_FIREFOX:
            self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, "test_firefox_switchcontentwindow",
                            self.env.test_method_name + "_" + self.env.time_stamp)
        else:
            self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, "test_chrome_switchcontentwindow",
                            self.env.test_method_name + "_" + self.env.time_stamp)

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
