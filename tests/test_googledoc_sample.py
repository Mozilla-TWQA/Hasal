import os
import time
import lib.helper.captureHelper as captureHelper
from lib.perfBaseTest import PerfBaseTest


class TestGoogleDocSample(PerfBaseTest):

    def setUp(self):
        super(TestGoogleDocSample, self).setUp()
        time.sleep(5)
        captureHelper.capture_screen(self.env, self.env.video_output_sample_1_fp, self.env.img_sample_dp,
                                     self.env.img_output_sample_1_fn)

    def test_chrome_load(self):
        os.system("bash thirdParty/runsikulix -r tests/simple_script_1_chrome.sikuli")
        assert(True)

    def tearDown(self):
        time.sleep(5)
        captureHelper.capture_screen(self.env, self.env.video_output_sample_2_fp, self.env.img_sample_dp,
                                     self.env.img_output_sample_2_fn)
        super(TestGoogleDocSample, self).tearDown()
