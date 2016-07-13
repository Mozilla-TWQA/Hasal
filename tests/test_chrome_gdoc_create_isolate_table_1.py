from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        self.pre_run_script = "test_chrome_gdoc_read_blank_page"
        self.pre_run_script_test_url_id = "TEST_TARGET_ID_BLANK_PAGE"
        super(TestSikuli, self).setUp()

    def test_chrome_gdoc_create_isolate_table_1(self):
        self.sikuli_status = self.sikuli.run_test( self.env.test_method_name,
                        self.env.test_method_name + "_" + self.env.time_stamp, test_url=self.test_url)
