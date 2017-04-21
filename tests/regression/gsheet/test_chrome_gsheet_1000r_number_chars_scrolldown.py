from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_chrome_gsheet_1000r_number_chars_scrolldown(self):
        self.test_url = self.global_config['gsuite']['gsheet-test-url-spec'] % self.global_config['gsuite']['gsheet-1000r-number-enchar-100formula']
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.test_url, script_dp=self.env.test_script_py_dp)
