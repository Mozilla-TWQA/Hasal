import time
from lib.perfBaseTest import PerfBaseTest

class TestGoogleDocSample(PerfBaseTest):

    def setUp(self):
        super(TestGoogleDocSample, self).setUp()
        self.docUrl = "https://docs.google.com/document/d/1HXDdOQuxQiX1bSrpAs4hJfTaim1iLO_xB01nokb0wT0/edit?usp=sharing"
        self.driver.get(self.docUrl)
        time.sleep(5)
        self.video_recording_obj.capture_screen(self.video_output_sample_1_fp, self.img_sample_dp, self.img_output_sample_1_fn)

    #def test_firefox_load(self):
    #    # Recording start marker
    #    self.driver.execute_script("var teststart = function(){document.getElementById('docs-branding-logo').style.backgroundColor = 'red'}; teststart()");
    #    time.sleep(5)
    #    timings = self.driver.execute_script("return window.performance.timing")
    #    self.dumpToJson(timings, self.profile_timing_json_fp)
    #    assert(True)

    def test_chrome_load(self):
        # Recording start marker
        self.driver.execute_script("var teststart = function(){document.getElementById('docs-branding-logo').style.backgroundColor = 'red'}; teststart()");
        time.sleep(5)
        timings = self.driver.execute_script("return window.performance.timing")
        self.dumpToJson(timings, self.profile_timing_json_fp)
        assert(True)

    def tearDown(self):
        self.video_recording_obj.capture_screen(self.video_output_sample_2_fp, self.img_sample_dp, self.img_output_sample_2_fn)
        super(TestGoogleDocSample, self).tearDown()
