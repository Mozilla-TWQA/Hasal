from base import BaseProfiler
import codecs
import pyperclip


class GeckoProfiler(BaseProfiler):

    def start_recording(self):
        pass

    def stop_recording(self, **kwargs):
        if self.browser_type == self.env.DEFAULT_BROWSER_TYPE_FIREFOX:
            self.sikuli.run_test("test_firefox_profile",
                                 self.env.profile_timing_bin_fp)
            data = pyperclip.paste()

            encoding_list = ["utf8"]
            encoding = "latin_1"
            for ec in encoding_list:
                if ec in self.env.test_name:
                    encoding = ec

            try:
                with codecs.open(self.env.profile_timing_bin_fp, "w+", encoding) as f:
                    f.write(data)
            except:
                # if failed, then try to save profile data to utf-8
                with codecs.open(self.env.profile_timing_bin_fp, "w+", 'utf8') as f:
                    f.write(data)
        else:
            pass
