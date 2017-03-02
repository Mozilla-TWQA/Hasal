from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_firefox_facebook_post_link(self):
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.env.TEST_FB_FIRST_WALL, script_dp=self.env.test_script_py_dp, args_list=["https://www.mozilla.org/en-US/"])
