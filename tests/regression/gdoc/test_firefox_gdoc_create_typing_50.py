from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        self.pre_run_script = "test_firefox_gdoc_read_blank_page"
        self.pre_run_script_test_url_id = self.global_config['gsuite']['gdoc-blank-page']  # copy from environment
        super(TestSikuli, self).setUp()

    def test_firefox_gdoc_create_typing_50(self):
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.test_url, script_dp=self.env.test_script_py_dp)
