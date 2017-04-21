from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        self.set_variable(test_target=self.global_config['gsuite']['gdoc-1-page-content-with-table'])
        super(TestSikuli, self).setUp()

    def test_firefox_gdoc_read_basic_table_1(self):
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.test_url, script_dp=self.env.test_script_py_dp)
