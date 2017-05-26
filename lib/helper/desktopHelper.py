import sys
import importlib
import subprocess
from ..common.windowController import WindowObject
from ..common.environment import Environment
from ..common.logConfig import get_logger

logger = get_logger(__name__)


# This is to load browser class according to test engine ( Sikuli / Webdriver / ... )
def _load_browser_class(type="sikuli"):
    # type = webdriver / sikuli
    if type == 'webdriver':
        chrome_class = getattr(importlib.import_module("lib.browser.webdriverChrome"), "BrowserChrome")
        firefox_class = getattr(importlib.import_module("lib.browser.webdriverFirefox"), "BrowserFirefox")
    elif type == 'sikuli':
        chrome_class = getattr(importlib.import_module("lib.browser.chrome"), "BrowserChrome")
        firefox_class = getattr(importlib.import_module("lib.browser.firefox"), "BrowserFirefox")

    return chrome_class, firefox_class


def launch_browser(browser_type, **kwargs):
    env = kwargs['env']
    exec_config = kwargs['exec_config']
    # default set engine type as sikuli since type would not be specified in perfBaseTest
    if 'type' in kwargs:
        engine_type = kwargs['type']
    else:
        engine_type = 'sikuli'
    profiler_list = kwargs['profiler_list']
    enabled_profiler_list = [x for x in profiler_list if profiler_list[x]['enable'] is True]
    profile_path = None

    chrome_class, firefox_class = _load_browser_class(engine_type)

    if browser_type == env.DEFAULT_BROWSER_TYPE_CHROME:
        profile_path = env.chrome_profile_path
        if env.PROFILER_FLAG_CHROMETRACING in enabled_profiler_list:
            browser_obj = chrome_class(exec_config['browser-height'], exec_config['browser-width'],
                                       tracing_path=env.chrome_tracing_file_fp,
                                       profile_path=profile_path)
        else:
            browser_obj = chrome_class(exec_config['browser-height'], exec_config['browser-width'], profile_path=profile_path)
    elif browser_type == env.DEFAULT_BROWSER_TYPE_FIREFOX:
        profile_path = env.firefox_profile_path
        if env.PROFILER_FLAG_FXTRACELOGGER in enabled_profiler_list:
            browser_obj = firefox_class(exec_config['browser-height'], exec_config['browser-width'], tracelogger=True,
                                        profile_path=profile_path)
        else:
            browser_obj = firefox_class(exec_config['browser-height'], exec_config['browser-width'],
                                        profile_path=profile_path)

    browser_obj.launch()
    return browser_obj, profile_path


def get_browser_name_list(browser_type):
    if browser_type == Environment.DEFAULT_BROWSER_TYPE_FIREFOX:
        # This is to ensure all kinds of firefox we supported can be properly moved.
        if sys.platform == 'darwin':
            return ['Firefox.app', 'FirefoxNightly.app']
        else:
            return ['Mozilla Firefox', 'Nightly']
    elif browser_type.lower() == Environment.DEFAULT_BROWSER_TYPE_CHROME:
        if sys.platform == 'darwin':
            return ['Google Chrome.app', 'Chrome.app']
        else:
            return ['Google Chrome']
    else:
        if sys.platform == 'darwin':
            return ['{}.app'.format(browser_type)]
        else:
            return [browser_type]


def close_browser(browser_type):
    window_title_list = get_browser_name_list(browser_type)
    window_obj = WindowObject(window_title_list)
    window_obj.close_window()


# TODO: need to finish webdriver way to get version
def get_browser_version(browser_type, engine_type='sikuli'):
    chrome_class, firefox_class = _load_browser_class(engine_type)

    if browser_type == Environment.DEFAULT_BROWSER_TYPE_FIREFOX:
        browser_obj = firefox_class(0, 0)
    else:
        browser_obj = chrome_class(0, 0)
    return_version = browser_obj.get_version()
    return return_version


# TODO: external usage should be considered once all settings from environment are extracted
def lock_window_pos(browser_type, exec_config={}, height_adjustment=0, width_adjustment=0):
    window_title_list = get_browser_name_list(browser_type)
    # Moving window by strings from window_title
    window_obj = WindowObject(window_title_list)

    # First launch or just move position only need to get browser size from settings
    if not height_adjustment and not width_adjustment:
        if not exec_config:
            height = Environment.DEFAULT_BROWSER_HEIGHT
            width = Environment.DEFAULT_BROWSER_WIDTH
        else:
            height = exec_config['browser-height']
            width = exec_config['browser-width']
    else:
        window_obj.get_window_rect()
        browser_width = window_obj.rect[2]
        browser_height = window_obj.rect[3]
        height = browser_height + height_adjustment
        width = browser_width + width_adjustment
    window_obj.move_window_pos(0, 0, window_height=height, window_width=width)
    return height, width


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


def adjust_viewport(browser_type, viewport, exec_config):
    height_adjustment = exec_config['viewport-height'] - viewport['height']
    width_adjustment = exec_config['viewport-width'] - viewport['width']
    height, width = lock_window_pos(browser_type, exec_config, height_adjustment, width_adjustment)
    return height, width


def is_expected_viewport(viewport, exec_config):
    if viewport['height'] == exec_config['viewport-height'] and viewport['width'] == exec_config['viewport-width']:
        return True
    else:
        return False


def is_above_half_viewport(viewport, exec_config):
    half_viewport_height = exec_config['viewport-height'] * 0.5
    half_viewport_width = exec_config['viewport-width'] * 0.5
    if viewport['height'] >= half_viewport_height and viewport['width'] >= half_viewport_width:
        return True
    else:
        return False
