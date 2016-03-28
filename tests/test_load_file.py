import time
from lib.perfBaseTest import PerfBaseTest

class TestGoogleDocSample(PerfBaseTest):

    def setUp(self):
        super(TestGoogleDocSample, self).setUp()
        self.docUrl = "https://docs.google.com/a/mozilla.com/document/d/1YNxUZPc7xB4OtnxnRLMIKlagMzSOh3_uggp2WCz3aww/edit?usp=sharing"
        self.driver.get(self.docUrl)
        self.driver.execute_script("var teststart = function(){document.getElementById('docs-branding-logo').style.backgroundColor = 'red'}; teststart()");
        time.sleep(5)
        self.video_recording_obj.capture_screen(self.video_output_sample_1_fp, self.img_sample_dp, self.img_output_sample_1_fn)

    def test_firefox_load(self):
        self.logfile()

    def test_chrome_load(self):
        self.logfile()

    def logfile(self):
        # Recording start marker
        
        ########## Test case session ########################
        self.docUrl = "https://docs.google.com/document/d/1EpYUniwtLvBbZ4ECgT_vwGUfTHKnqSWi7vgNJQBemFk/edit?usp=sharing"
        self.driver.get(self.docUrl)
        #####################################################
        time.sleep(5)
        self.video_recording_obj.capture_screen(self.video_output_sample_2_fp, self.img_sample_dp, self.img_output_sample_2_fn)
        timings = self.driver.execute_script("return window.performance.timing")
        self.dumpToJson(timings, self.profile_timing_json_fp)
        assert(True)

    def tearDown(self):
        super(TestGoogleDocSample, self).tearDown()