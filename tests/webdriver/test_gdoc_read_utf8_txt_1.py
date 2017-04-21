from lib.webdriverBaseTest import WebdriverBaseTest


class TestGdocReadUTF8txt1(WebdriverBaseTest):

    def setUp(self):
        self.set_variable(test_target=self.global_config['gsuite']['gdoc-1-page-content-with-utf8-txt'])
        super(TestGdocReadUTF8txt1, self).setUp()

    def test_gdoc_read_utf8_txt_1(self):
        self.driver.get(self.test_url)
