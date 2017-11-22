import os
from lib.speedometerBaseTest import SpeedometerBaseTest


class TestSikuli(SpeedometerBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_chrome_power_gadget_sunflower_mp4(self):
        """
        Reference file: http://distribution.bbb3d.renderfarming.net/video/mp4/bbb_sunflower_1080p_30fps_normal.mp4
        10 m 35 s
        """
        target_file_name = 'bbb_sunflower_1080p_30fps_normal.mp4'
        test_url = os.path.join(os.path.dirname(os.path.realpath(__file__)), target_file_name)

        self.round_status = self.sikuli.run_test(self.env.test_name,
                                                 self.env.output_name,
                                                 test_target=test_url,
                                                 script_dp=self.env.test_script_py_dp)
