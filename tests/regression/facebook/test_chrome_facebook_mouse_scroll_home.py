from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_chrome_facebook_mouse_scroll_home(self):
        self.sikuli_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.env.TEST_FB_HOME, script_dp=self.env.test_script_py_dp)
