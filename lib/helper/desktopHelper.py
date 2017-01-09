import subprocess
import sys
import lib.sikuli  # NOQA
import tempfile
import zipfile
import os
import time
import json
from ..browser.chrome import BrowserChrome
from ..browser.firefox import BrowserFirefox
from ..common.windowController import WindowObject
from ..common.imageTool import ImageTool
from ..common.environment import Environment


def extract_profile_data(input_profile_path):
    tmp_dir = tempfile.mkdtemp()
    profile_dir_name = input_profile_path.split(".")[0].split(os.sep)[-1]
    with zipfile.ZipFile(input_profile_path) as zh:
        zh.extractall(tmp_dir)
    return_path = os.path.join(tmp_dir, profile_dir_name)
    return return_path


def create_profile(prefs={}):
    tmp_dir = tempfile.mkdtemp(prefix='firefoxprofile_')
    if sys.platform == 'linux2':
        os.system('firefox -createprofile "{} {}" -silent'.format(os.path.basename(tmp_dir), tmp_dir))
    else:
        if sys.platform == 'darwin':
            firefox_cmd = '/Applications/Firefox.app/Contents/MacOS/firefox'
        else:
            firefox_cmd = 'firefox'
        os.system('{} --profile {} -silent'.format(firefox_cmd, tmp_dir))
    print('[Info] Create Profile: {}'.format(tmp_dir))

    if prefs:
        print('[Info] Prefs {}'.format(prefs))
        prefs_list = []
        prefs_js_file = os.path.join(tmp_dir, 'prefs.js')
        for k, v in prefs.items():
            print('[Info] load {} : {}'.format(k, v))
            if isinstance(v, bool) or isinstance(v, int):
                prefs_list.append('user_pref("{}", {});'.format(str(k), str(v).lower()))
            elif isinstance(v, str) or isinstance(v, unicode):
                prefs_list.append('user_pref("{}", "{}");'.format(str(k), str(v)))
        # Skip First Run page
        prefs_list.append('user_pref("toolkit.startup.last_success", {});'.format(int(time.time())))
        prefs_list.append('user_pref("browser.startup.homepage_override.mstone", "ignore");')

        prefs_settings = '\n'.join(prefs_list)
        print('[Info] Writing prefs into {}:\n{}'.format(prefs_js_file, prefs_settings))

        with open(prefs_js_file, 'a') as prefs_f:
            prefs_f.write('\n' + prefs_settings)

    return tmp_dir


def launch_browser(browser_type, **kwargs):
    env = kwargs['env']
    enabled_profiler_list = kwargs['enabled_profiler_list']
    profile_path = None

    if env.PROFILER_FLAG_CHROMETRACING in enabled_profiler_list:
        if browser_type == env.DEFAULT_BROWSER_TYPE_CHROME:
            browser_obj = BrowserChrome(env.DEFAULT_BROWSER_HEIGHT, env.DEFAULT_BROWSER_WIDTH,
                                        tracing_path=env.chrome_tracing_file_fp)
        else:
            profile_path = create_profile(prefs=env.firefox_settings_prefs)
            browser_obj = BrowserFirefox(env.DEFAULT_BROWSER_HEIGHT, env.DEFAULT_BROWSER_WIDTH,
                                         profile_path=profile_path)
    elif env.PROFILER_FLAG_FXTRACELOGGER in enabled_profiler_list:
        if browser_type == env.DEFAULT_BROWSER_TYPE_FIREFOX:
            if kwargs['profile_path'] is not None:
                profile_path = extract_profile_data(kwargs['profile_path'])
            else:
                profile_path = create_profile(prefs=env.firefox_settings_prefs)
            browser_obj = BrowserFirefox(env.DEFAULT_BROWSER_HEIGHT, env.DEFAULT_BROWSER_WIDTH, tracelogger=True,
                                         profile_path=profile_path)
        else:
            browser_obj = BrowserChrome(env.DEFAULT_BROWSER_HEIGHT, env.DEFAULT_BROWSER_WIDTH)
    elif kwargs['profile_path'] is not None:
        if browser_type == env.DEFAULT_BROWSER_TYPE_FIREFOX:
            profile_path = extract_profile_data(kwargs['profile_path'])
            browser_obj = BrowserFirefox(env.DEFAULT_BROWSER_HEIGHT, env.DEFAULT_BROWSER_WIDTH, profile_path=profile_path)
        else:
            browser_obj = BrowserChrome(env.DEFAULT_BROWSER_HEIGHT, env.DEFAULT_BROWSER_WIDTH)
    else:
        if browser_type == env.DEFAULT_BROWSER_TYPE_FIREFOX:
            profile_path = create_profile(prefs=env.firefox_settings_prefs)
            browser_obj = BrowserFirefox(env.DEFAULT_BROWSER_HEIGHT, env.DEFAULT_BROWSER_WIDTH,
                                         profile_path=profile_path)
        else:
            browser_obj = BrowserChrome(env.DEFAULT_BROWSER_HEIGHT, env.DEFAULT_BROWSER_WIDTH)

    browser_obj.launch()
    return profile_path


def get_browser_version(browser_type):
    if browser_type == Environment.DEFAULT_BROWSER_TYPE_FIREFOX:
        browser_obj = BrowserFirefox(0, 0)
    else:
        browser_obj = BrowserChrome(0, 0)
    return_version = browser_obj.get_version()
    return return_version


def lock_window_pos(browser_type, height_adjustment=0, width_adjustment=0):
    window_title = None
    if browser_type == Environment.DEFAULT_BROWSER_TYPE_FIREFOX:
        if sys.platform == "darwin":
            window_title = ["Firefox.app", "FirefoxNightly.app"]
        else:
            # This is to ensure all kinds of firefox we supported can be properly moved.
            window_title = ["Mozilla Firefox", "Nightly"]

    else:
        if sys.platform == "darwin":
            window_title = ["Chrome.app"]
        else:
            window_title = ["Google Chrome"]

    # Moving window by strings from window_title
    height = Environment.DEFAULT_BROWSER_HEIGHT + height_adjustment
    width = Environment.DEFAULT_BROWSER_WIDTH + width_adjustment
    for window_name in window_title:
        window_obj = WindowObject(window_name)
        if window_obj.move_window_pos(0, 0, window_height=height, window_width=width):
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


def adjust_viewport(browser_type, img_sample_dp, img_sample_name):
    img_obj = ImageTool()
    img_sample_fp = os.path.join(img_sample_dp, img_sample_name)
    viewport = img_obj.find_image_viewport(img_sample_fp)
    height_adjustment = Environment.DEFAULT_VIEWPORT_HEIGHT - viewport['height']
    width_adjustment = Environment.DEFAULT_VIEWPORT_WIDTH - viewport['width']
    lock_window_pos(browser_type, height_adjustment, width_adjustment)
