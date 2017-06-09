from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()
        self.set_configs(self.config_name.INDEX,
                         self.extract_platform_dep_settings({"win32": {"7": {"compare-threshold": 0.02},
                                                                       '10': {'compare-threshold': 0.02}}}))

    def test_firefox_facebook_ail_type_composerbox_1_txt(self):
        self.round_status = self.sikuli.run_test(self.env.test_name,
                                                 self.env.output_name,
                                                 test_target=self.env.TEST_FB_HOME,
                                                 script_dp=self.env.test_script_py_dp,
                                                 args_list=[self.env.img_sample_dp,
                                                            self.env.img_output_sample_1_fn,
                                                            self.exec_config['video-recording-width'],
                                                            self.exec_config['video-recording-height'],
                                                            self.env.DEFAULT_TIMESTAMP])
