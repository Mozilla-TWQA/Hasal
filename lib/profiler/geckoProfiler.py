from ..helper.desktopHelper import DEFAULT_BROWSER_TYPE_FIREFOX
from base import BaseProfiler
import codecs
import pyperclip


class GeckoProfiler(BaseProfiler):

    def start_recording(self):
        pass

    def stop_recording(self, **kwargs):
        if self.browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
            self.sikuli.run(self.env.sikuli_path, self.env.hasal_dir, "test_firefox_profile",
                            self.env.profile_timing_bin_fp)
            data = pyperclip.paste()

            encoding_list = ["utf8"]
            encoding = "latin_1"
            for ec in encoding_list:
                if ec in self.test_method_name:
                    encoding = ec

            with codecs.open(self.env.profile_timing_bin_fp, "w+", encoding) as f:
                f.write(data)
        else:
            pass
