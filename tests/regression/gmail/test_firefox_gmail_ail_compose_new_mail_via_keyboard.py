from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_firefox_gmail_ail_compose_new_mail_via_keyboard(self):
        """
        This performance case should open the keyboard shortcuts feature.
        Steps:
            1. open GMail
            2. Click the Settings Gear on top-right side
            3. Go to General tab
            4. Enable Keyboard Shortcuts
            5. Save Changes
        """
        self.test_url = self.global_config['gsuite']['gmail']['test-url']

        self.round_status = self.sikuli.run_test(self.env.test_name,
                                                 self.env.output_name,
                                                 test_target=self.test_url,
                                                 script_dp=self.env.test_script_py_dp,
                                                 args_list=[self.env.img_sample_dp,
                                                            self.env.img_output_sample_1_fn,
                                                            self.env.DEFAULT_VIDEO_RECORDING_WIDTH,
                                                            self.env.DEFAULT_VIDEO_RECORDING_HEIGHT,
                                                            self.env.DEFAULT_TIMESTAMP])
