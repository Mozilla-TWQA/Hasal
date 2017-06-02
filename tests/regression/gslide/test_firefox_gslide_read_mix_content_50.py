from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_firefox_gslide_read_mix_content_50(self):
        self.test_url = self.global_config['gsuite']['test-target-google-drive'] + self.global_config['gsuite']['gslide-50-page-mix-content']
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.test_url, script_dp=self.env.test_script_py_dp)
