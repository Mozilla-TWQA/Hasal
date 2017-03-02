
from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_firefox_topsites_www_ask_com_launch(self):
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target="http://www.ask.com/web?q=mozilla", script_dp=self.env.test_script_py_dp)
