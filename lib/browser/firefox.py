import os
from base import BrowserBase


class BrowserFirefox(BrowserBase):
    ubuntu_firefox_command = "firefox"
    darwin_firefox_command = "/Applications/Firefox.app/Contents/MacOS/firefox"

    def get_browser_settings(self, **kwargs):
        self.browser_process = "firefox"
        self.process_name = "firefox"
        if self.current_platform_name == "darwin":
            self.command = self.darwin_firefox_command
        elif self.current_platform_name == "linux2":
            self.command = self.ubuntu_firefox_command
        else:
            self.command = self.ubuntu_firefox_command
        self.launch_cmd = [self.command, "-height", self.window_size_height, "-width",
                           self.windows_size_width]

        if "profile_path" in kwargs:
            self.launch_cmd.extend(["--profile", kwargs['profile_path']])

        if "tracelogger" in kwargs:
            self.test_env = os.environ.copy()
            self.test_env['TLLOG'] = "default"
            self.test_env['TLOPTIONS'] = "EnableMainThread,EnableOffThread,EnableGraph"

    def get_version_command(self):
        return [self.command, "-v"]
