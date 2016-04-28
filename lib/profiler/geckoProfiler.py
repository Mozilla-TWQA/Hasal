from ..helper.desktopHelper import DEFAULT_BROWSER_TYPE_FIREFOX
from base import BaseProfiler


class GeckoProfiler(BaseProfiler):

    def start_recording(self):
        pass

    def stop_recording(self):
        if self.browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
            self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, "test_firefox_profile",
                            self.env.profile_timing_bin_fp)
        else:
            pass
