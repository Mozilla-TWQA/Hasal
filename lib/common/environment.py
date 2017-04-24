import os
import time
import json
import platform
import logConfig
from urlparse import urljoin

logger = logConfig.get_logger(__name__)


class Environment(object):

    DEFAULT_HASAL_DIR = os.getcwd()
    DEFAULT_THIRDPARTY_DIR = os.path.join(DEFAULT_HASAL_DIR, "thirdParty")
    DEFAULT_EXTENSIONS_DIR = os.path.join(DEFAULT_THIRDPARTY_DIR, "extensions")
    DEFAULT_GECKODRIVER_DIR = os.path.join(DEFAULT_THIRDPARTY_DIR, "geckodriver")
    DEFAULT_OUTPUT_DIR = os.path.join(DEFAULT_HASAL_DIR, "output")
    DEFAULT_PROFILE_DIR = os.path.join(DEFAULT_HASAL_DIR, "resource")
    DEFAULT_UPLOAD_DIR = os.path.join(DEFAULT_HASAL_DIR, "upload")
    DEFAULT_FLOW_DIR = os.path.join(DEFAULT_HASAL_DIR, "flows")
    DEFAULT_VIDEO_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "videos")
    DEFAULT_PROFILE_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "profiles")
    DEFAULT_WAVEFORM_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "waveform")
    DEFAULT_IMAGE_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images")
    DEFAULT_IMAGE_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images", "output")
    DEFAULT_IMAGE_SAMPLE_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images", "sample")
    DEFAULT_GECKO_PROFILER_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR, "geckoprofiler-signed.xpi")
    DEFAULT_CHROME_DRIVER_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR, "chromedriver")
    DEFAULT_SIKULI_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR, "sikulix") if os.path.isfile(os.path.join(DEFAULT_THIRDPARTY_DIR, "sikulix", "runsikulix")) else os.path.join(DEFAULT_THIRDPARTY_DIR)
    DEFAULT_TEST_RESULT = os.path.join(DEFAULT_HASAL_DIR, "result.json")
    DEFAULT_STAT_RESULT = os.path.join(DEFAULT_HASAL_DIR, "stat.json")
    DEFAULT_TIMESTAMP = os.path.join(DEFAULT_HASAL_DIR, "timestamp.json")
    INITIAL_TIMESTAMP_NAME = 'initial_timestamp'

    DEFAULT_BROWSER_POS_X = 0
    DEFAULT_BROWSER_POS_Y = 0
    DEFAULT_BROWSER_WIDTH = 1024
    DEFAULT_BROWSER_HEIGHT = 780
    DEFAULT_BROWSER_TYPE_FIREFOX = "firefox"
    DEFAULT_BROWSER_TYPE_CHROME = "chrome"
    if platform.system().lower() == "darwin":
        DEFAULT_VIDEO_RECORDING_FPS = 40
        DEFAULT_VIEWPORT_WIDTH = 800
        DEFAULT_VIEWPORT_HEIGHT = 600
    else:
        DEFAULT_VIDEO_RECORDING_FPS = 60
        DEFAULT_VIEWPORT_WIDTH = 1024
        DEFAULT_VIEWPORT_HEIGHT = 768
    DEFAULT_VIDEO_RECORDING_POS_X = 72
    DEFAULT_VIDEO_RECORDING_POS_Y = 125
    DEFAULT_VIDEO_RECORDING_WIDTH = min(DEFAULT_BROWSER_WIDTH + 100, 1920)
    if platform.system().lower() == "darwin":
        DEFAULT_VIDEO_RECORDING_HEIGHT = min(DEFAULT_BROWSER_HEIGHT + 120, 900)
    else:
        DEFAULT_VIDEO_RECORDING_HEIGHT = min(DEFAULT_BROWSER_HEIGHT + 180, 1080)

    PROFILE_FILE_NAME_AUTOSAVEHAR_GECKOPROFILER = "GeckoProfilerAutoSaveHAR.zip"
    PROFILE_NAME_HAR_PROFILER = "HarProfiler"
    PROFILE_NAME_GECKO_PROFILER = "GeckoProfiler"

    PROFILER_FLAG_AVCONV = "AvconvProfiler"
    PROFILER_FLAG_OBS = "ObsProfiler"
    PROFILER_FLAG_HAREXPORT = "HarProfiler"
    PROFILER_FLAG_GECKOPROFILER = "GeckoProfiler"
    PROFILER_FLAG_CHROMETRACING = "ChromeTracing"
    PROFILER_FLAG_MITMDUMP = "MitmDumpProfiler"
    PROFILER_FLAG_FXTRACELOGGER = "TraceloggerProfiler"

    TEST_FB_HOME = "https://www.facebook.com/"
    TEST_FB_MESSAGES = urljoin(TEST_FB_HOME, "messages")
    TEST_FB_TEXT_GROUP = urljoin(TEST_FB_HOME, "groups/testmoztext/")
    TEST_FB_IMAGE_GROUP = urljoin(TEST_FB_HOME, "groups/testmozimage/")
    TEST_FB_VIDEO_GROUP = urljoin(TEST_FB_HOME, "groups/testmozvideo/")
    TEST_FB_FIRST_WALL = urljoin(TEST_FB_HOME, "profile.php?id=100013326969542")
    TEST_FB_SECOND_WALL = urljoin(TEST_FB_HOME, "profile.php?id=100013275014638")
    TEST_FB_MIX_CONTENT_POST = "https://goo.gl/PZNikF"
    TEST_FB_VIDEO_POST = "https://goo.gl/z3iwyh"
    TEST_FB_URL_POST = "https://goo.gl/fxja5z"

    def __init__(self, test_method_name, test_method_doc, sikuli_script_name=None):
        self.time_stamp = str(int(time.time()))
        self.test_method_name = test_method_name
        self.test_method_doc = test_method_doc
        self.hasal_dir = self.DEFAULT_HASAL_DIR
        self.sikuli_path = self.DEFAULT_SIKULI_PATH
        self.run_sikulix_cmd_path = os.path.join(self.sikuli_path, "runsikulix")
        if sikuli_script_name:
            self.test_name = sikuli_script_name
        else:
            self.test_name = test_method_name
        self.test_script_py_dp = os.getenv("TEST_SCRIPT_PY_DIR_PATH")
        if os.getenv("SIKULI_SCRIPT_PATH"):
            script_path_list = os.getenv("SIKULI_SCRIPT_PATH").split(os.sep)
            test_sikuli_name = self.test_name + ".sikuli"
            if test_sikuli_name in script_path_list:
                self.web_app_name = script_path_list[script_path_list.index(test_sikuli_name) - 1]
            else:
                self.web_app_name = script_path_list[-3]
        else:
            self.web_app_name = self.test_script_py_dp.split(os.sep)[-1]

        self.output_name = self.test_name + "_" + self.time_stamp
        self.flow_file_fp = self.test_name + ".flow"
        self.video_output_fp = os.path.join(self.DEFAULT_VIDEO_OUTPUT_DIR, self.output_name + ".mkv")
        self.converted_video_output_fp = os.path.join(self.DEFAULT_VIDEO_OUTPUT_DIR, self.output_name + ".mp4")
        self.video_output_sample_1_fp = os.path.join(self.DEFAULT_VIDEO_OUTPUT_DIR, self.output_name + "_sample_1.mkv")
        self.video_output_sample_2_fp = os.path.join(self.DEFAULT_VIDEO_OUTPUT_DIR, self.output_name + "_sample_2.mkv")
        self.img_sample_dp = os.path.join(self.DEFAULT_IMAGE_SAMPLE_DIR, self.output_name)
        self.img_output_dp = os.path.join(self.DEFAULT_IMAGE_OUTPUT_DIR, self.output_name)
        self.img_output_sample_1_fn = self.output_name + "_sample_1.bmp"
        self.img_output_sample_2_fn = self.output_name + "_sample_2.bmp"
        self.img_output_crop_fn = self.output_name + "_sample_3.jpg"
        self.profile_timing_json_fp = os.path.join(self.DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + "_timing.json")
        self.profile_har_file_fp = os.path.join(self.DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + ".har")
        self.profile_tracelogger_zip_fp = os.path.join(self.DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + "_tracelogger.zip")
        self.chrome_tracing_file_fp = os.path.join(self.DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + "_tracing.json")
        self.recording_log_fp = os.path.join(self.hasal_dir, "recording.log")
        self.waveform_fp = os.path.join(self.DEFAULT_WAVEFORM_OUTPUT_DIR, self.output_name + "_waveform_info.json")

        self.firefox_settings_json = os.getenv('FIREFOX_CONFIG_FP')
        self.firefox_settings_env = {}
        self.firefox_settings_prefs = {}
        self.firefox_settings_extensions = {}
        self.firefox_settings_cookies = {}
        if os.path.exists(self.firefox_settings_json):
            with open(self.firefox_settings_json) as firefox_settings_fh:
                firefox_settings_obj = json.load(firefox_settings_fh)
                self.firefox_settings_env = firefox_settings_obj.get('env', {})
                self.firefox_settings_prefs = firefox_settings_obj.get('prefs', {})
                self.firefox_settings_extensions = firefox_settings_obj.get('extensions', {})
                self.firefox_settings_cookies = firefox_settings_obj.get('cookies', {})
        self.firefox_profile_path = os.getenv('FIREFOX_PROFILE_PATH')
        self.chrome_profile_path = os.getenv('CHROME_PROFILE_PATH')

        if self.firefox_settings_env:
            for k, v in self.firefox_settings_env.items():
                logger.info('Set environment variable: {}={}'.format(k, v))
                if isinstance(v, bool) or isinstance(v, int):
                    os.putenv(k, str(int(v)))
                elif isinstance(v, str) or isinstance(v, unicode):
                    os.putenv(k, str(v))

    def init_output_dir(self):
        # Init output folder
        for chk_dir in [self.DEFAULT_OUTPUT_DIR, self.DEFAULT_VIDEO_OUTPUT_DIR, self.DEFAULT_PROFILE_OUTPUT_DIR,
                        self.DEFAULT_IMAGE_DIR, self.DEFAULT_IMAGE_OUTPUT_DIR, self.DEFAULT_IMAGE_SAMPLE_DIR,
                        self.DEFAULT_WAVEFORM_OUTPUT_DIR]:
            if not os.path.exists(chk_dir):
                os.mkdir(chk_dir)

    def get_browser_type(self):
        result = "firefox"
        test_name_list = self.test_name.split("_")
        if len(test_name_list) > 2:
            result = test_name_list[1].lower()
        return result
