from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        self.set_variable(test_target=self.env.TEST_TARGET_ID_10_PAGE_CONTENT_WITH_TXT)
        super(TestSikuli, self).setUp()

    def test_firefox_gdoc_page10_typea(self):
        self.sikuli_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.test_url,
                                                  script_dp=self.env.test_script_py_dp,
                                                  args_list=[self.env.img_sample_dp, self.env.img_output_sample_1_fn,
                                                             self.env.DEFAULT_VIDEO_RECORDING_WIDTH,
                                                             self.env.DEFAULT_VIDEO_RECORDING_HEIGHT,
                                                             self.env.DEFAULT_TIMESTAMP])
