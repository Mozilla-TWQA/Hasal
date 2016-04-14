import unittest
import helper.desktopHelper as desktopHelper
import helper.resultHelper as resultHelper
import helper.captureHelper as captureHelper
from common.environment import Environment
from helper.profilerHelper import Profilers


class PerfBaseTest(unittest.TestCase):

    profiler_list = [{"path": "lib.profiler.avconvProfiler", "name": "AvconvProfiler"}]

    def setUp(self):
        # Init environment variables
        self.env = Environment(self._testMethodName)

        # Init output dirs
        self.env.init_output_dir()

        # get browser type
        self.browser_type = self.env.get_browser_type()

        # Start video recordings
        self.profilers = Profilers(self.env)
        self.profilers.start_profiling(self.profiler_list)

        # minimize all windows
        desktopHelper.minimize_window()

        # launch browser
        desktopHelper.launch_browser(self.browser_type)

    def tearDown(self):

        # Stop profiler and save profile data
        self.profilers.stop_profiling()

        # Stop browser
        desktopHelper.stop_browser(self.browser_type, self.env)

        # output result
        resultHelper.result_calculation(self.env)
