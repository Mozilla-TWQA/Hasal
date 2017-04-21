import os
from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        self.set_variable(crop_data={"range": [(70, 65), (920, 100)],
                                     "target": os.path.join(self.env.img_sample_dp, self.env.img_output_sample_2_fn),
                                     "output": os.path.join(self.env.img_sample_dp, self.env.img_output_crop_fn)})
        super(TestSikuli, self).setUp()

    def test_firefox_facebook_load_bluebar(self):
        self.round_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.env.TEST_FB_HOME, script_dp=self.env.test_script_py_dp)
