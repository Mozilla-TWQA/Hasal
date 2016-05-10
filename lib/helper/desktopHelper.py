import subprocess
import platform
import lib.sikuli
import tempfile
import zipfile
import os
from ..browser.chrome import BrowserChrome
from ..browser.firefox import BrowserFirefox

DEFAULT_BROWSER_POS_X = 0
DEFAULT_BROWSER_POS_Y = 0
DEFAULT_BROWSER_WIDTH = 1200
DEFAULT_BROWSER_HEIGHT = 980
DEFAULT_BROWSER_TYPE_FIREFOX = "firefox"
DEFAULT_BROWSER_TYPE_CHROME = "chrome"


def extract_profile_data(input_profile_path):
    tmp_dir = tempfile.mkdtemp()
    profile_dir_name = input_profile_path.split(".")[0].split(os.sep)[-1]
    with zipfile.ZipFile(input_profile_path) as zh:
        zh.extractall(tmp_dir)
    return_path = os.path.join(tmp_dir, profile_dir_name)
    return return_path


def launch_browser(browser_type, input_profile_path=None):
    if input_profile_path is not None:
        profile_path = extract_profile_data(input_profile_path)
    else:
        profile_path = input_profile_path

    if browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
        browser_obj = BrowserFirefox(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH, profile_path)
    else:
        browser_obj = BrowserChrome(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH, profile_path)
    browser_obj.launch()
    return profile_path

def stop_browser(browser_type, env):
    # This could sometime cause firefox/chrome safe mode issue
    # if browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
    #     browser_obj = BrowserFirefox(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
    # else:
    #     browser_obj = BrowserChrome(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
    # browser_obj.stop()
    print browser_type
    lib.sikuli.Sikuli().close_browser(browser_type, env)


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
