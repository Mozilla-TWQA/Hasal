
from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_chrome_topsites_twitter_com_launch(self):
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target="https://twitter.com/hashtag/news", script_dp=self.env.test_script_py_dp)
