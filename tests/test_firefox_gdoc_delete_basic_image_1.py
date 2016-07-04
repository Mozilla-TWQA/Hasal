from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()
        self.test_url, self.test_url_id = self.target_helper.clone_target(self.env.TEST_TARGET_ID_1_PAGE_CONTENT_WITH_IMAGE,
                                                                          self.env.output_name)

    def test_firefox_gdoc_delete_basic_image_1(self):
        self.sikuli_status = self.sikuli.run_test( self.env.test_method_name,
                                             self.env.test_method_name + "_" + self.env.time_stamp,
                                             test_url=self.test_url)
