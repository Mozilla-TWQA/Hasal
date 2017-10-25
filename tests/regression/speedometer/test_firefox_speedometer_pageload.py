from lib.speedometerBaseTest import SpeedometerBaseTest


class TestSikuli(SpeedometerBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_firefox_speedometer_pageload(self):
        test_url = "http://browserbench.org/Speedometer/"
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=test_url,
                                                 script_dp=self.env.test_script_py_dp)
