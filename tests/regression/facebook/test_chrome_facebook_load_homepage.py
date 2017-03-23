import os
import time
from lib.perfBaseTest import PerfBaseTest
from lib.common.logConfig import get_logger


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_chrome_facebook_load_homepage(self):
        start_time = time.time()
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.env.TEST_FB_HOME, script_dp=self.env.test_script_py_dp)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger = get_logger(os.path.basename(__file__), os.getenv("ENABLE_ADVANCE"))
        logger.debug("Action Time Elapsed: [%s]" % elapsed_time)
