from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_firefox_gsheet_100r_number_chars_chart_100formula(self):
        self.test_url = self.global_config['gsuite']['gsheet-test-url-spec'] % self.global_config['gsuite']['gsheet-100r-number-enchar-chart-100formula']
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.test_url, script_dp=self.env.test_script_py_dp)
