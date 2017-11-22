import os
from lib.speedometerBaseTest import SpeedometerBaseTest


class TestSikuli(SpeedometerBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_firefox_power_gadget_sunflower_webm(self):
        """
        Reference file: https://upload.wikimedia.org/wikipedia/commons/8/88/Big_Buck_Bunny_alt.webm
        9 m 57 s
        """
        target_file_name = 'Big_Buck_Bunny_alt.webm'
        test_url = os.path.join(os.path.dirname(os.path.realpath(__file__)), target_file_name)

        self.round_status = self.sikuli.run_test(self.env.test_name,
                                                 self.env.output_name,
                                                 test_target=test_url,
                                                 script_dp=self.env.test_script_py_dp)
