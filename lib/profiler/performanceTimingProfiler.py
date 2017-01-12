from base import BaseProfiler
import json
import codecs
import pyperclip


class PerformanceTimingProfiler(BaseProfiler):

    def start_recording(self):
        pass

    def stop_recording(self, **kwargs):
        if self.browser_type == self.env.DEFAULT_BROWSER_TYPE_FIREFOX:
            self.sikuli.run_test("test_firefox_timing",
                                 self.env.profile_timing_json_fp)
        else:
            self.sikuli.run_test("test_chrome_timing",
                                 self.env.profile_timing_json_fp)

        data = pyperclip.paste()
        try:
            json_data = json.loads(data)
            data = json.dumps(json_data, indent=4)
        except:
            pass

        with codecs.open(self.env.profile_timing_json_fp, "w+", 'utf8') as f:
            f.write(data)
