from ..helper.desktopHelper import DEFAULT_BROWSER_TYPE_FIREFOX
from base import BaseProfiler


class PerformanceTimingProfiler(BaseProfiler):

    def start_recording(self):
        pass

    def stop_recording(self):
        if self.browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
            self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, "test_firefox_timing",
                            self.env.test_method_name + "_" + self.env.time_stamp)
        else:
            self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, "test_chrome_timing",
                            self.env.test_method_name + "_" + self.env.time_stamp)
