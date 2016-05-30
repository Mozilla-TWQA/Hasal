import platform
from base import BrowserBase


class BrowserChrome(BrowserBase):

    def get_browser_settings(self):
        ubuntu_chrome_command = 'google-chrome'
        darwin_chrome_command = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
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
            self.launch_cmd = [ubuntu_chrome_command,
                               "--window-size=" + str(self.windows_size_width) + "," + str(self.window_size_height)]