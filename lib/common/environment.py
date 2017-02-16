import os
import time
import json
import platform
import logConfig

logger = logConfig.get_logger(__name__)


class Environment(object):

    DEFAULT_HASAL_DIR = os.getcwd()
    DEFAULT_THIRDPARTY_DIR = os.path.join(os.getcwd(), "thirdParty")
    DEFAULT_EXTENSIONS_DIR = os.path.join(os.getcwd(), "thirdParty", "extensions")
    DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "output")
    DEFAULT_PROFILE_DIR = os.path.join(os.getcwd(), "resource")
    DEFAULT_UPLOAD_DIR = os.path.join(os.getcwd(), "upload")
    DEFAULT_FLOW_DIR = os.path.join(os.getcwd(), "flows")
    DEFAULT_VIDEO_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "videos")
    DEFAULT_PROFILE_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "profiles")
    DEFAULT_WAVEFORM_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "waveform")
    DEFAULT_IMAGE_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images")
    DEFAULT_IMAGE_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images", "output")
    DEFAULT_IMAGE_SAMPLE_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images", "sample")
    DEFAULT_GECKO_PROFILER_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR, "geckoprofiler-signed.xpi")
    DEFAULT_CHROME_DRIVER_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR, "chromedriver")
    DEFAULT_SIKULI_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR, "sikulix") if os.path.isfile(os.path.join(DEFAULT_THIRDPARTY_DIR, "sikulix", "runsikulix")) else os.path.join(DEFAULT_THIRDPARTY_DIR)
    DEFAULT_TEST_RESULT = os.path.join(os.getcwd(), "result.json")
    DEFAULT_STAT_RESULT = os.path.join(os.getcwd(), "stat.json")

    DEFAULT_BROWSER_POS_X = 0
    DEFAULT_BROWSER_POS_Y = 0
    DEFAULT_BROWSER_WIDTH = 1024
    DEFAULT_BROWSER_HEIGHT = 800
    DEFAULT_BROWSER_TYPE_FIREFOX = "firefox"
    DEFAULT_BROWSER_TYPE_CHROME = "chrome"
    if platform.system().lower() == "darwin":
        DEFAULT_VIDEO_RECORDING_FPS = 40
        DEFAULT_VIEWPORT_WIDTH = 800
        DEFAULT_VIEWPORT_HEIGHT = 600
    else:
        DEFAULT_VIDEO_RECORDING_FPS = 50
        DEFAULT_VIEWPORT_WIDTH = 1024
        DEFAULT_VIEWPORT_HEIGHT = 768
    DEFAULT_VIDEO_RECORDING_POS_X = 72
    DEFAULT_VIDEO_RECORDING_POS_Y = 125
    DEFAULT_VIDEO_RECORDING_WIDTH = DEFAULT_BROWSER_WIDTH + 100
    DEFAULT_VIDEO_RECORDING_HEIGHT = DEFAULT_BROWSER_HEIGHT + 110
    IMG_FILE_EXTENSION = ['.jpg', '.png', '.jpeg']

    SEARCH_TARGET_VIEWPORT = 'viewport'
    SEARCH_TARGET_TAB_VIEW = 'tab_view'
    SEARCH_TARGET_BROWSER = 'browser'
    # event points need to follow the order of appearing time from searching
    BROWSER_VISUAL_EVENT_POINTS = {'backward_search': [{'event': 'first_paint', 'search_target': SEARCH_TARGET_VIEWPORT},
                                                       {'event': 'start', 'search_target': SEARCH_TARGET_TAB_VIEW}],
                                   'forward_search': [
                                       {'event': 'viewport_visual_complete', 'search_target': SEARCH_TARGET_VIEWPORT},
                                       {'event': 'end', 'search_target': SEARCH_TARGET_BROWSER}]}

    DEFAULT_TEST_TARGET_FOLDER_URI = "0B6LePZQnd-uOTHhJNEhTN1pqYm8"
    GSHEET_TEST_TARGET_FOLDER_URI = "0B6LePZQnd-uOdkNVTkItaG96WkU"

    TEST_TARGET_ID_3_PAGE_CONTENT_WITH_TXT_TABLE_IMAGE = "1fTGfC2e5hD590gNChcolhOyXFBRV1O2zdfbVLU44Y84"
    TEST_TARGET_ID_1_PAGE_CONTENT_WITH_UTF8_TXT = "1ktU9DnreProcMXa0L5PBCateh-xJYbKqsf-3TgwAJhI"
    TEST_TARGET_ID_1_PAGE_CONTENT_WITH_IMAGE = "1JFLaWO-X2upQcYvPQBT59VQJmHngai9u7K3WPG1ll6Y"
    TEST_TARGET_ID_1_PAGE_CONTENT_WITH_TABLE = "1d49NaEpY9G9laZY_OPYfYdjngeAvcGNEPMTEVsW76js"
    TEST_TARGET_ID_1_PAGE_CONTENT_WITH_TXT = "1YpQyum1kME8lMPiaQuxa8O9-beuife0WTmpIlspZn2w"
    TEST_TARGET_ID_50_PAGE_CONTENT_WITH_TXT_TABLE_IMAGE = "1eR7Tvo_H6Rnz68mXp_FBw555uyGb76NbB_1sPDrQzBs"
    TEST_TARGET_ID_100_PAGE_CONTENT_WITH_TXT_TABLE_IMAGE = "1antDLK_Un8DCtbO-GodBbI7mTaeqrTgoIgdbF2sP8Tg"
    TEST_TARGET_ID_200_PAGE_CONTENT_WITH_TXT_TABLE_IMAGE = "1EPSmGqm2r4Qq42B4t1VOYacjTlL0JVuC8JSlUvoIhss"
    TEST_TARGET_ID_BLANK_PAGE = "1ORZOuLyxehup7IhBQk02t0qycDr0VcCa3ciXfwTdEmk"
    TEST_TARGET_ID_3_FIND_REPLACE = "1jv-uypgBinghqgi5P2t2oqD2e-lhJcdzF2I5RM0dUI4"
    TEST_TARGET_ID_10_FORMAT = "1dng0q8nKz1t_wc3CyKwV62jY9NNyNmeuxdG_OmDpeX0"

    TEST_TARGET_ID_10_PAGE_CONTENT_WITH_TXT = "1qFOWeHhCIo6njlYgs3qqfv1MaDmt6vbINyOHgbEZbNY"

    TEST_TARGET_ID_3_PAGE_CONTENT_WITH_TXT_TABLE_IMAGE_INCREASING = "1N0UMuDKFNlxFNLbhyfOAsc-6iOh1pS_hTMZ0A1JFNOI"
    TEST_TARGET_ID_100_PAGE_CONTENT_WITH_TXT_TABLE_IMAGE_INCREASING = "13glV5sea6fqMP1ZWmxAiRgXdMI-hOLmbWlndOsJiaKM"

    PROFILE_FILE_NAME_AUTOSAVEHAR_GECKOPROFILER = "GeckoProfilerAutoSaveHAR.zip"
    PROFILE_NAME_HAR_PROFILER = "HarProfiler"
    PROFILE_NAME_GECKO_PROFILER = "GeckoProfiler"

    PROFILER_FLAG_AVCONV = "AvconvProfiler"
    PROFILER_FLAG_HAREXPORT = "HarProfiler"
    PROFILER_FLAG_GECKOPROFILER = "GeckoProfiler"
    PROFILER_FLAG_CHROMETRACING = "ChromeTracing"
    PROFILER_FLAG_MITMDUMP = "MitmDumpProfiler"
    PROFILER_FLAG_FXTRACELOGGER = "TraceloggerProfiler"

    TEST_FB_HOME = "https://www.facebook.com/"
    TEST_FB_TEXT_GROUP = os.path.join(TEST_FB_HOME, "groups/testmoztext/")
    TEST_FB_IMAGE_GROUP = os.path.join(TEST_FB_HOME, "groups/testmozimage/")
    TEST_FB_VIDEO_GROUP = os.path.join(TEST_FB_HOME, "groups/testmozvideo/")
    TEST_FB_FIRST_WALL = os.path.join(TEST_FB_HOME, "profile.php?id=100013326969542")
    TEST_FB_SECOND_WALL = os.path.join(TEST_FB_HOME, "profile.php?id=100013275014638")
    TEST_FB_MIX_CONTENT_POST = "http://goo.gl/PZNikF"
    TEST_FB_VIDEO_POST = "http://goo.gl/z3iwyh"
    TEST_FB_URL_POST = "http://goo.gl/fxja5z"

    GSHEET_TEST_URL_SPEC = "https://docs.google.com/spreadsheets/d/%s"
    TEST_TARGET_ID_100R_NUMBER_ENCHAR = "1_vIBHZgVLdEPbo8DrJwbSKNVTCcyfDehOzv9yAXHJ2k"
    TEST_TARGET_ID_100R_NUMBER_UTF8CHAR = "1vOKw5Z_-NDo88UzkWL4e0Rq2bHzs5COCF_VcmjYsABU"
    TEST_TARGET_ID_1000R_NUMBER_ENCHAR = "1VrcKk4P09LQfVdJ2r9mb9yUWeQkYbzupwd8rSwPA0og"
    TEST_TARGET_ID_1000R_NUMBER_ENCHAR_100FORMULA = "1IhDNQbZMa7_o_3T2UzUhinoz6tGzvbm0ylUIABeXdyw"
    TEST_TARGET_ID_100R_NUMBER_ENCHAR_CHART = "1URnWqI5s5TOO24XY9uzFmC0cAK7YILX_vHshZicfz58"
    TEST_TARGET_ID_100R_NUMBER_ENCHAR_IMAGE = "1maNKDPAqQE1AJ0eOX79rDZ5TICiGBzifNLkJe_WHjGY"
    TEST_TARGET_ID_100R_DIFFERENT_COLOR = "1thrpmc3B-ap_kGl9D5oGV6iTbZI-AeNAXPE6WHWpm_k"
    TEST_TARGET_ID_1000R_NUMBER_ENCHAR_1000FORMULA = "1WAroSR8zAWowHN2nVhj6oVDlgkR1sbu2BABZjZdpipE"
    TEST_TARGET_ID_100R_NUMBER_ENCHAR_CHART_100FORMULA = "1aWyKYtMx08F8rCa83quOk7iVZzGYvZAp5Y5rHRzEtuo"
    TEST_TARGET_ID_100R_NUMBER_ENCHAR_100FORMULA_10TABS = "1tespXUQoX3xuqiR5iwGE9ofaN7uzapMDpEcXG5VSYZc"
    TEST_TARGET_ID_100R_NUMBER_ENCHAR_CHART_10TABS = "1l_43dqzfsY-Qy-bO3vCW7BedQjWuzoI7p1j8M-uKVA0"
    TEST_TARGET_ID_100R_NUMBER_ENCHAR_IMAGE_10TABS = "1YZ68juV1D4uL16Off0RYZbXvhYSuG90KgNXbmZJIO1o"
    TEST_TARGET_ID_100R_NUMBER_UTF8CHAR_10TABS = "1__DF-ilgSIhkQrotazWSQZvlOc3UBISCCaDNbxPLLN8"
    TEST_TARGET_ID_100R_DIFFERENT_COLOR_10TABS = "1CPBaq71I-8FoGsbC8VETFWZdS_FdVFYPA63Tn53Kuko"

    TEST_TARGET_GOOGLE_DRIVE = "https://drive.google.com/open?id="
    TEST_TARGET_ID_SLIDE_1_PAGE_BLANK = "1wdPUMvSWJN8mJnMhcpJ8Q3vXTU6x2N3Mw3iAqHC8dhU"
    TEST_TARGET_ID_SLIDE_1_PAGE_TEXT = "1LLMATDFqINPkhXAO4reEvewD6Yu8IxE_WCpKefFYvS0"
    TEST_TARGET_ID_SLIDE_1_PAGE_UTF8_TEXT = "1tb7HxLXkwTt2-Bp3zrXQUbfoW8XAskq9aZrIfqZOYEY"
    TEST_TARGET_ID_SLIDE_1_PAGE_IMAGE_CHART = "1OHTiIuQypImqcrPrGyXi3B1afZ-m-5r4tdC-SjiaeeU"
    TEST_TARGET_ID_SLIDE_1_PAGE_TABLE = "1VvEZ9DSIlbjXXXY01wAccMdaF2q9wA1Zx21-nuH3KQc"
    TEST_TARGET_ID_SLIDE_1_PAGE_SHAPE = "1N58xZ3iu9jXtf-dAibVfdDGJaO620zJ_sZdS3p0goLc"
    TEST_TARGET_ID_SLIDE_2_PAGE_ANIMATION = "1XEMltvPJyK6W9RE0sh9xikpkVvL5N7Szbd4HLx7XPGE"
    TEST_TARGET_ID_SLIDE_5_PAGE_IMAGE_CHART = "1ifP0QuDC69F-TVyH6cV8_-6eiosStFSZYicsWEaGiLY"
    TEST_TARGET_ID_SLIDE_5_PAGE_MIX_CONTENT = "1OYe9litCbERoaIk6f4bq4yuEW__G1kZnjxVI7iPzaa0"
    TEST_TARGET_ID_SLIDE_10_PAGE_UTF8_TEXT = "1_g4xl1lSLNQQPYsaJt7mK3NH727SsD3GRdy0NIebF2A"
    TEST_TARGET_ID_SLIDE_10_PAGE_MIX_CONTENT = "1XLZRP0IQ5RoG7AdgaU2mMq6LAkFcggQRTLSMdGH6Yxo"
    TEST_TARGET_ID_SLIDE_30_PAGE_MIX_CONTENT = "1j3jzuxNYqsbbja31R3ozPOqGg-D6vStr97G5EYS8RhY"
    TEST_TARGET_ID_SLIDE_50_PAGE_MIX_CONTENT = "1weuhf0CT_z-R1yxQm9HoKiNHBNOMoeaGi4LxE1JOYOo"

    if platform.system().lower() == "darwin":
        DEFAULT_VIDEO_RECORDING_DISPLAY = "1"
    else:
        DEFAULT_VIDEO_RECORDING_DISPLAY = ":0.0+" + str(DEFAULT_VIDEO_RECORDING_POS_X) + "," + str(
            DEFAULT_VIDEO_RECORDING_POS_X)
    DEFAULT_VIDEO_RECORDING_CODEC = "h264_fast"

    def __init__(self, test_method_name, test_method_doc, sikuli_script_name=None):
        self.DEFAULT_OUTLIER_CHECK_POINT = int(os.getenv("MAX_RUN"))
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
        self.img_output_sample_1_fn = self.output_name + "_sample_1.jpg"
        self.img_output_sample_2_fn = self.output_name + "_sample_2.jpg"
        self.img_output_crop_fn = self.output_name + "_sample_3.jpg"
        self.profile_timing_json_fp = os.path.join(self.DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + "_timing.json")
        self.profile_timing_bin_fp = os.path.join(self.DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + ".bin")
        self.profile_har_file_fp = os.path.join(self.DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + ".har")
        self.profile_tracelogger_zip_fp = os.path.join(self.DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + "_tracelogger.zip")
        self.chrome_tracing_file_fp = os.path.join(self.DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + "_tracing.json")
        self.recording_log_fp = os.path.join(self.hasal_dir, "recording.log")
        self.waveform_fp = os.path.join(self.DEFAULT_WAVEFORM_OUTPUT_DIR, self.output_name + "_waveform_info.json")

        self.firefox_settings_json = os.getenv('FIREFOX_SETTINGS')
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
