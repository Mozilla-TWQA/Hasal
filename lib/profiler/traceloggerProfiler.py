import os
import re
import sys
import time
import zipfile
from base import BaseProfiler


class TraceLoggerProfiler(BaseProfiler):

    def zipFiles(self, dir_path, file_list, output_fp):
        try:
            import zlib  # NOQA
            compression = zipfile.ZIP_DEFLATED
        except:
            compression = zipfile.ZIP_STORED

        zf = zipfile.ZipFile(output_fp, mode='w')
        try:
            for file_name in file_list:
                file_path = os.path.join(dir_path, file_name)
                zf.write(file_path, compress_type=compression)
        finally:
            zf.close()

    def start_recording(self):
        pass

    def stop_recording(self, **kwargs):
        if sys.platform == "darwin":
            # Make sure logger data could be stored properly, we only support firefox that's why we hard-coded
            os.system("osascript -e 'quit app \"firefox\"'")
        else:
            self.sikuli.close_browser(self.browser_type)

        # Make sure logger data is updated!
        time.sleep(5)

        if sys.platform == "win32":
            dir_path = os.getcwd()
            files = [f for f in os.listdir(dir_path) if re.match(r'tl-.*\.[json|tl]', f)]
        else:
            dir_path = "/tmp"
            files = [f for f in os.listdir(dir_path) if re.match(r'tl-.*\.[json|tl]', f)]

        self.zipFiles(dir_path, files, self.env.profile_tracelogger_zip_fp)
