from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        self.set_variable(test_target=self.global_config['gsuite']['gsheet-1000r-number-enchar-1000formula'])
        self.set_variable(target_folder=self.global_config['gsuite']['gsheet-test-target-folder-uri'])
        super(TestSikuli, self).setUp()

    def test_chrome_gsheet_1000r_number_chars_1000formula_modifycell(self):
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.test_url, script_dp=self.env.test_script_py_dp)
