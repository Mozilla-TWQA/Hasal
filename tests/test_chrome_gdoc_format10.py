from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        self.set_variable(test_target=self.env.TEST_TARGET_ID_BLANK_PAGE)
        super(TestSikuli, self).setUp()

    def test_chrome_gdoc_format10(self):
        self.sikuli_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_url=self.test_url)
