import platform
from base import BrowserBase


class BrowserFirefox(BrowserBase):

    def get_browser_settings(self):
        ubuntu_firefox_command = "firefox"
        current_platform_name = platform.system().lower()

        if current_platform_name == "darwin":
            self.browser_process = "firefox"
            self.process_name = "firefox"
            self.launch_cmd = [ubuntu_firefox_command, "-height", self.window_size_height, "-width",
                               self.windows_size_width]
        elif current_platform_name == "linux":
            self.browser_process = "firefox"
            self.process_name = "firefox"
            self.launch_cmd = [ubuntu_firefox_command, "-height", self.window_size_height, "-width",
                               self.windows_size_width]
        else:
            self.browser_process = "firefox"
            self.process_name = "firefox"
            self.launch_cmd = [ubuntu_firefox_command, "-height", self.window_size_height, "-width",
                               self.windows_size_width]

        if self.profile_path is not None:
            self.launch_cmd.extend(["--profile", self.profile_path])
