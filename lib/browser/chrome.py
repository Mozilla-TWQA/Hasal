from base import BrowserBase
import subprocess
from ..common.logConfig import get_logger

logger = get_logger(__name__)


class BrowserChrome(BrowserBase):
    windows_chrome_command = 'chrome'
    ubuntu_chrome_command = 'google-chrome'
    darwin_chrome_command = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    windows_language_postfix = '--lang=en-US'

    def get_browser_settings(self, **kwargs):
        default_tracing_capture_period = 900  # sec
        self.browser_process = "chrome"
        self.process_name = "chrome"
        if self.current_platform_name == "darwin":
            self.command = self.darwin_chrome_command
        elif self.current_platform_name == "linux2":
            self.command = self.ubuntu_chrome_command
        else:
            self.command = self.windows_chrome_command

        self.launch_cmd = [self.command,
                           "--window-size=" + str(self.windows_size_width) + "," + str(self.window_size_height)]

        if self.current_platform_name == "win32":
            self.launch_cmd.extend([self.windows_language_postfix])
        elif self.current_platform_name == "linux2":
            self.test_env['LANGUAGE'] = "en-US"

        profile_path = kwargs.get('profile_path', '')
        if profile_path:
            logger.info('Running Chrome with profile: {}'.format(profile_path))
            self.launch_cmd.extend(["--user-data-dir=%s" % profile_path])
        else:
            logger.info('Running Chrome with default profile.')

        if "tracing_path" in kwargs:
            self.launch_cmd.extend(["--trace-startup", "--trace-startup-file=" + kwargs['tracing_path'],
                                    "--trace-startup-duration=" + str(default_tracing_capture_period)])

    def get_version_command(self):
        if self.current_platform_name == "darwin" or self.current_platform_name == "linux2":
            return [[self.command, "--version"]]
        else:
            return [['reg', 'query', 'HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon', '/v', 'version'],
                    ["reg", "query",
                     "HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome",
                     "/v", "DisplayVersion"]]

    def get_version(self):
        commands = self.get_version_command()
        return_version = '0'
        if self.current_platform_name == "darwin" or self.current_platform_name == "linux2":
            for cmd in commands:
                if subprocess.call(cmd) == 0:
                    return_version = subprocess.check_output(cmd).splitlines()[0].split(" ")[2]
                    break
        else:
            for cmd in commands:
                if subprocess.call(cmd) == 0:
                    return_version = subprocess.check_output(cmd).splitlines()[2].split()[2]
        return return_version
