# please:
#     1. replace "browser" to be firefox, chrome, ie, edge, or the browser you are using
#     2. make sure you have (Google Drive String) replaced
import time
import lib.helper.captureHelper as captureHelper
from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()
        self.test_url, self.test_url_id = self.target_helper.clone_target("(Google Drive String)",
                                                                          self.env.output_name)
        time.sleep(3)
        self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, "test_browser_switchcontentwindow",
                        self.env.test_method_name + "_" + self.env.time_stamp)

        time.sleep(5)
        captureHelper.capture_screen(self.env, self.env.video_output_sample_1_fp, self.env.img_sample_dp,
                                     self.env.img_output_sample_1_fn)

    def test_browser_template(self):
        self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, self.env.test_method_name,
                        self.env.test_method_name + "_" + self.env.time_stamp, test_url=self.test_url)
        assert(True)

    def tearDown(self):
        time.sleep(3)
        self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, "test_browser_defocuscontentwindow",
                        self.env.test_method_name + "_" + self.env.time_stamp)
        time.sleep(3)
        captureHelper.capture_screen(self.env, self.env.video_output_sample_2_fp, self.env.img_sample_dp,
                                     self.env.img_output_sample_2_fn)

        super(TestSikuli, self).tearDown()
