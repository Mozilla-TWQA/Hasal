from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        self.set_configs(self.config_name.EXEC, {"browser-width": 1380, 'viewport-width': 1366})
        self.set_configs(self.config_name.EXEC, self.get_new_recording_size())
        super(TestSikuli, self).setUp()
        self.set_configs(self.config_name.INDEX,
                         self.extract_platform_dep_settings(
                             {'win32': {'7': {'search-margin': 2, 'compare-threshold': 0.007},
                                        '10': {'search-margin': 2, 'compare-threshold': 0.007}}}))

    def test_chrome_facebook_ail_click_open_chat_tab_emoji(self):
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.env.TEST_FB_FIRST_WALL,
                                                 script_dp=self.env.test_script_py_dp,
                                                 args_list=[self.env.img_sample_dp, self.env.img_output_sample_1_fn,
                                                            self.exec_config['video-recording-width'],
                                                            self.exec_config['video-recording-height'],
                                                            self.env.DEFAULT_TIMESTAMP])
