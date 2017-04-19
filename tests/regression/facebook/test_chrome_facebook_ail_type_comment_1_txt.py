from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        index_config = {"platform-dep-settings": {"win32": {"compare-threshold": 0.003}}}
        self.set_configs("index_config", index_config, True)
        super(TestSikuli, self).setUp()

    def test_chrome_facebook_ail_type_comment_1_txt(self):
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.env.TEST_FB_HOME,
                                                 script_dp=self.env.test_script_py_dp,
                                                 args_list=[self.env.img_sample_dp, self.env.img_output_sample_1_fn,
                                                            self.env.DEFAULT_VIDEO_RECORDING_WIDTH,
                                                            self.env.DEFAULT_VIDEO_RECORDING_HEIGHT,
                                                            self.env.DEFAULT_TIMESTAMP])
