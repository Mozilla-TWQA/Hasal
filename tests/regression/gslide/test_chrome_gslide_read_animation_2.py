from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_chrome_gslide_read_animation_2(self):
        self.test_url = self.env.TEST_TARGET_GOOGLE_DRIVE + self.env.TEST_TARGET_ID_SLIDE_2_PAGE_ANIMATION
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.test_url, script_dp=self.env.test_script_py_dp)
