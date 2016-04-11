import os
import sys
import time
import lib.sikuli as sikuli
import lib.helper.captureHelper as captureHelper
from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()
        time.sleep(5)
        captureHelper.capture_screen(self.env, self.env.video_output_sample_1_fp, self.env.img_sample_dp,
                                     self.env.img_output_sample_1_fn)
        self.sikuli = sikuli.Sikuli()

    def test_chrome_load_file(self):
        print self.env.sikuli_path, self.env.hasal_dir, self.env.test_method_name, self.env.time_stamp
        self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, self.env.test_method_name, self.env.time_stamp)
        assert(True)

    def test_chrome_gdoc_pagedown(self):
        print self.env.sikuli_path, self.env.hasal_dir, self.env.test_method_name, self.env.time_stamp
        self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, self.env.test_method_name, self.env.time_stamp)
        assert(True)

    def test_firefox_load_file(self):
        print self.env.sikuli_path, self.env.hasal_dir, self.env.test_method_name, self.env.time_stamp
        self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, self.env.test_method_name, self.env.time_stamp)
        assert(True)

    def test_firefox_gdoc_pagedown(self):
        print self.env.sikuli_path, self.env.hasal_dir, self.env.test_method_name, self.env.time_stamp
        self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, self.env.test_method_name, self.env.time_stamp)
        assert(True)

    def tearDown(self):
        time.sleep(5)
        captureHelper.capture_screen(self.env, self.env.video_output_sample_2_fp, self.env.img_sample_dp,
                                     self.env.img_output_sample_2_fn)
        super(TestSikuli, self).tearDown()
