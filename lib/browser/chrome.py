import platform
from base import BrowserBase


class BrowserChrome(BrowserBase):

    def get_browser_settings(self, **kwargs):
        windows_chrome_command = 'chrome'
        ubuntu_chrome_command = 'google-chrome'
        darwin_chrome_command = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        default_tracing_capture_period = 900 #sec
        current_platform_name = platform.system().lower()

        if current_platform_name == "darwin":
            self.browser_process = "chrome"
            self.process_name = "chrome"
            self.launch_cmd = [darwin_chrome_command,
                               "--window-size=" + str(self.windows_size_width) + "," + str(self.window_size_height)]
        elif current_platform_name == "linux":
            self.browser_process = "chrome"
            self.process_name = "chrome"
            self.launch_cmd = [ubuntu_chrome_command,
                               "--window-size=" + str(self.windows_size_width) + "," + str(self.window_size_height)]
        else:
            self.browser_process = "chrome"
            self.process_name = "chrome"
            self.launch_cmd = [windows_chrome_command,
                               "--window-size=" + str(self.windows_size_width) + "," + str(self.window_size_height)]

        if "tracing_path" in kwargs:
            self.launch_cmd.extend(["--trace-startup", "--trace-startup-file="+kwargs['tracing_path'], "--trace-startup-duration="+str(default_tracing_capture_period)])