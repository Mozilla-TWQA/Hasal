from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        self.set_variable(test_target=self.env.TEST_TARGET_ID_1000R_NUMBER_ENCHAR)
        self.set_variable(target_folder=self.env.GSHEET_TEST_TARGET_FOLDER_URI)
        super(TestSikuli, self).setUp()

    def test_firefox_gsheet_1000r_number_chars_1000formula_deletecell(self):
        self.sikuli_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.test_url, script_dp=self.env.test_script_py_dp)
