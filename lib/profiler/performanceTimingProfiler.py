from ..helper.desktopHelper import DEFAULT_BROWSER_TYPE_FIREFOX
from base import BaseProfiler


class PerformanceTimingProfiler(BaseProfiler):

    def start_recording(self):
        pass

    def stop_recording(self, **kwargs):
        if self.browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
            self.sikuli.run_test( "test_firefox_timing",
                            self.env.profile_timing_json_fp)
        else:
            self.sikuli.run_test( "test_chrome_timing",
                            self.env.profile_timing_json_fp)
