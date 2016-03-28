import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from lib.perfBaseTest import PerfBaseTest

class TestGoogleDocSample(PerfBaseTest):

    def setUp(self):
        super(TestGoogleDocSample, self).setUp()
        self.docUrl = "https://docs.google.com/document/d/1V17WzeUGbUTc4oqqS3IvnRLCC9Xs79p6CeDyKo0LBq0/edit"
        self.driver.get(self.docUrl)
        self.driver.execute_script("var teststart = function(){document.getElementById('docs-branding-logo').style.backgroundColor = 'red'}; teststart()");
        time.sleep(5)
        self.video_recording_obj.capture_screen(self.video_output_sample_1_fp, self.img_sample_dp, self.img_output_sample_1_fn)

    def test_firefox_load(self):
        self.pagedown()

    def test_chrome_load(self):
        self.pagedown()

    def pagedown(self):
        page = self.driver.find_element_by_xpath('//div[@class="kix-appview-editor"]')
        for p in range(100):
            page.send_keys(Keys.PAGE_DOWN)
        '''
        ## this is case for creating table
        element = self.driver.find_element_by_id("docs-table-menu")
        for i in range(1):
            ActionChains(self.driver).move_to_element(element).click().perform()
            ActionChains(self.driver).move_to_element(element).move_by_offset(0,35).perform()
            time.sleep(3)
            grid = self.driver.find_element_by_xpath('//div[@class="goog-dimension-picker"]')
            ##ActionChains(self.driver).drag_and_drop_by_offset(grid, 50, 50).perform()
            ##ActionChains(self.driver).move_to_element(grid).click_and_hold(on_element=None).move_by_offset(80, 80).release(on_element=None).perform()
            ActionChains(self.driver).move_to_element(grid).move_by_offset(200,200).perform()
            #grid.click()
        '''
        time.sleep(5)
        timings = self.driver.execute_script("return window.performance.timing")
        self.dumpToJson(timings, self.profile_timing_json_fp)
        assert(True)

    def tearDown(self):
        self.video_recording_obj.capture_screen(self.video_output_sample_2_fp, self.img_sample_dp, self.img_output_sample_2_fn)
        super(TestGoogleDocSample, self).tearDown()
