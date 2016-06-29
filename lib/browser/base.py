import psutil
import subprocess


class BrowserBase(object):
    browser_process = None
    launch_cmd = []
    process_name = None

    def __init__(self, window_size_height, windows_size_width, **kwargs):
        self.window_size_height = str(window_size_height)
        self.windows_size_width = str(windows_size_width)
        self.get_browser_settings(**kwargs)

    def get_browser_settings(self, **kwargs):
        pass

    def launch(self):
        print self.launch_cmd
        self.browser_process = subprocess.Popen(self.launch_cmd)

    def stop(self):
        for proc in psutil.process_iter():
            if proc.name().lower() == self.process_name:
                proc.send_signal(15)
