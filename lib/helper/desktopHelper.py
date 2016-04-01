import subprocess
import platform
from ..browser.chrome import BrowserChrome
from ..browser.firefox import BrowserFirefox

DEFAULT_BROWSER_POS_X = 0
DEFAULT_BROWSER_POS_Y = 0
DEFAULT_BROWSER_WIDTH = 1200
DEFAULT_BROWSER_HEIGHT = 980
DEFAULT_BROWSER_TYPE_FIREFOX = "firefox"
DEFAULT_BROWSER_TYPE_CHROME = "chrome"


def launch_browser(browser_type):
    if browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
        browser_obj = BrowserFirefox(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
    else:
        browser_obj = BrowserChrome(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
    browser_obj.launch()


def stop_browser(browser_type):
    if browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
        browser_obj = BrowserFirefox(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
    else:
        browser_obj = BrowserChrome(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
    browser_obj.stop()


def minimize_window():
    if platform.system().lower() == "linux":
        get_active_windows_cmd = "xdotool getactivewindow"
        minimize_all_windows_cmd = "xdotool getactivewindow key ctrl+super+d"
        org_window_id = subprocess.check_output(get_active_windows_cmd, shell=True)
        for try_cnt in range(3):
            subprocess.call(minimize_all_windows_cmd, shell=True)
            new_window_id = subprocess.check_output(get_active_windows_cmd, shell=True)
            if new_window_id != org_window_id:
                break
