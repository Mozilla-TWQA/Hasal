from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_chrome_facebook_load_mix_content(self):
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.env.TEST_FB_MIX_CONTENT_POST, script_dp=self.env.test_script_py_dp)
