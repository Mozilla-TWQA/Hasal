from base import BrowserBase
from ..common.logConfig import get_logger

logger = get_logger(__name__)


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

        profile_path = kwargs.get('profile_path', '')
        if profile_path:
            logger.info('Running Firefox with profile: {}'.format(profile_path))
            self.launch_cmd.extend(["--profile", profile_path])
        else:
            logger.info('Running Firefox with default profile.')

        if "tracelogger" in kwargs:
            self.test_env['TLLOG'] = "default"
            self.test_env['TLOPTIONS'] = "EnableMainThread,EnableOffThread,EnableGraph"

    def get_version_command(self):
        return [self.command, "-v"]
