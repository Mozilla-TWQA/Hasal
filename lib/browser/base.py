import sys
import psutil
import subprocess
from ..common.logConfig import get_logger

logger = get_logger(__name__)


class BrowserBase(object):
    browser_process = None
    launch_cmd = []
    process_name = None

    def __init__(self, window_size_height, windows_size_width, **kwargs):
        self.current_platform_name = sys.platform
        self.window_size_height = str(window_size_height)
        self.windows_size_width = str(windows_size_width)
        self.get_browser_settings(**kwargs)

    def get_browser_settings(self, **kwargs):
        pass

    def get_version_command(self):
        pass

    def launch(self):
        logger.debug("browser launch command:%s" % self.launch_cmd)
        if hasattr(self, "test_env"):
            self.browser_process = subprocess.Popen(self.launch_cmd, env=self.test_env)
        else:
            self.browser_process = subprocess.Popen(self.launch_cmd)

    def get_version(self):
        cmd = self.get_version_command()
        return_version = subprocess.check_output(cmd).splitlines()[0].split(" ")[2]
        return return_version

    def stop(self):
        for proc in psutil.process_iter():
            if proc.name().lower() == self.process_name:
                proc.send_signal(15)
