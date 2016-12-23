import subprocess
import sys
import lib.sikuli  # NOQA
import tempfile
import zipfile
import os
from ..browser.chrome import BrowserChrome
from ..browser.firefox import BrowserFirefox
from ..common.windowController import WindowObject

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


def launch_browser(browser_type, **kwargs):
    env = kwargs['env']
    enabled_profiler_list = kwargs['enabled_profiler_list']
    profile_path = None

    if env.PROFILER_FLAG_CHROMETRACING in enabled_profiler_list:
        if browser_type == DEFAULT_BROWSER_TYPE_CHROME:
            browser_obj = BrowserChrome(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH,
                                        tracing_path=env.chrome_tracing_file_fp)
        else:
            browser_obj = BrowserFirefox(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
    elif env.PROFILER_FLAG_FXTRACELOGGER in enabled_profiler_list:
        if browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
            if kwargs['profile_path'] is not None:
                profile_path = extract_profile_data(kwargs['profile_path'])
                browser_obj = BrowserFirefox(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH, tracelogger=True,
                                             profile_path=profile_path)
            else:
                browser_obj = BrowserFirefox(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH, tracelogger=True)
        else:
            browser_obj = BrowserChrome(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
    elif kwargs['profile_path'] is not None:
        if browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
            profile_path = extract_profile_data(kwargs['profile_path'])
            browser_obj = BrowserFirefox(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH, profile_path=profile_path)
        else:
            browser_obj = BrowserChrome(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
    else:
        if browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
            browser_obj = BrowserFirefox(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)
        else:
            browser_obj = BrowserChrome(DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH)

    browser_obj.launch()
    return profile_path


def get_browser_version(browser_type):
    if browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
        browser_obj = BrowserFirefox(0, 0)
    else:
        browser_obj = BrowserChrome(0, 0)
    return_version = browser_obj.get_version()
    return return_version


def lock_window_pos(browser_type):
    window_title = None
    if browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
        if sys.platform == "darwin":
            window_title = ["Firefox.app"]
        else:
            # This is to ensure all kinds of firefox we supported can be properly moved.
            window_title = ["Mozilla Firefox", "Nightly"]

    else:
        if sys.platform == "darwin":
            window_title = ["Chrome.app"]
        else:
            window_title = ["Google Chrome"]

    # Moving window by strings from window_title
    for window_name in window_title:
        window_obj = WindowObject(window_name)
        if window_obj.move_window_pos(0, 0, DEFAULT_BROWSER_HEIGHT, DEFAULT_BROWSER_WIDTH):
            break


def minimize_window():
    if sys.platform == "linux2":
        get_active_windows_cmd = "xdotool getactivewindow"
        minimize_all_windows_cmd = "xdotool getactivewindow key ctrl+super+d"
        org_window_id = subprocess.check_output(get_active_windows_cmd, shell=True)
        for try_cnt in range(3):
            subprocess.call(minimize_all_windows_cmd, shell=True)
            new_window_id = subprocess.check_output(get_active_windows_cmd, shell=True)
            if new_window_id != org_window_id:
                break
