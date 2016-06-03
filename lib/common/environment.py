import os
import time
import platform
from ..helper.desktopHelper import DEFAULT_BROWSER_TYPE_FIREFOX


class Environment(object):

    DEFAULT_HASAL_DIR = os.getcwd()
    DEFAULT_THIRDPARTY_DIR = os.path.join(os.getcwd(), "thirdParty")
    DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "output")
    DEFAULT_PROFILE_DIR = os.path.join(os.getcwd(), "resource")
    DEFAULT_VIDEO_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "videos")
    DEFAULT_PROFILE_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "profiles")
    DEFAULT_IMAGE_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images")
    DEFAULT_IMAGE_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images", "output")
    DEFAULT_IMAGE_SAMPLE_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images", "sample")
    DEFAULT_GECKO_PROFILER_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR, "geckoprofiler-signed.xpi")
    DEFAULT_CHROME_DRIVER_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR, "chromedriver")
    DEFAULT_SIKULI_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR, "sikulix") if os.path.isfile(os.path.join(DEFAULT_THIRDPARTY_DIR, "sikulix", "runsikulix")) else os.path.join(DEFAULT_THIRDPARTY_DIR)
    DEFAULT_TEST_RESULT = os.path.join(os.getcwd(), "result.json")
    DEFAULT_SIKULI_STATUS_RESULT = os.path.join(os.getcwd(), "sikuli_stat.txt")
    DEFAULT_TIME_LIST_COUNTER_RESULT = os.path.join(os.getcwd(), "time_list_counter.txt")

    DEFAULT_VIDEO_RECORDING_FPS = 90
    DEFAULT_VIDEO_RECORDING_POS_X = 72
    DEFAULT_VIDEO_RECORDING_POS_Y = 125
    DEFAULT_VIDEO_RECORDING_WIDTH = 1024
    DEFAULT_VIDEO_RECORDING_HEIGHT = 768

    DEFAULT_OUTLIER_CHECK_POINT = 30

    DEFAULT_TEST_TARGET_FOLDER_URI = "0B6LePZQnd-uOTHhJNEhTN1pqYm8"

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


    if platform.system().lower() == "darwin":
        DEFAULT_VIDEO_RECORDING_DISPLAY = "1"
    else:
        DEFAULT_VIDEO_RECORDING_DISPLAY = ":0.0+" + str(DEFAULT_VIDEO_RECORDING_POS_X) + "," + str(
            DEFAULT_VIDEO_RECORDING_POS_X)
    DEFAULT_VIDEO_RECORDING_CODEC = "h264_fast"

    def __init__(self, test_method_name, test_method_doc):
        self.time_stamp = str(int(time.time()))
        self.test_method_name = test_method_name
        self.test_method_doc = test_method_doc
        self.hasal_dir = self.DEFAULT_HASAL_DIR
        self.sikuli_path = self.DEFAULT_SIKULI_PATH
        self.output_name = test_method_name + "_" + self.time_stamp
        self.video_output_fp = os.path.join(self.DEFAULT_VIDEO_OUTPUT_DIR, self.output_name + ".mkv")
        self.video_output_sample_1_fp = os.path.join(self.DEFAULT_VIDEO_OUTPUT_DIR, self.output_name + "_sample_1.mkv")
        self.video_output_sample_2_fp = os.path.join(self.DEFAULT_VIDEO_OUTPUT_DIR, self.output_name + "_sample_2.mkv")
        self.img_sample_dp = os.path.join(self.DEFAULT_IMAGE_SAMPLE_DIR, self.output_name)
        self.img_output_dp = os.path.join(self.DEFAULT_IMAGE_OUTPUT_DIR, self.output_name)
        self.img_output_sample_1_fn = self.output_name + "_sample_1.jpg"
        self.img_output_sample_2_fn = self.output_name + "_sample_2.jpg"
        self.profile_timing_json_fp = os.path.join(self.DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + "_timing.json")
        self.profile_timing_bin_fp = os.path.join(self.DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + ".bin")
        self.profile_har_file_fp = os.path.join(self.DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + ".har")

    def init_output_dir(self):
        # Init output folder
        for chk_dir in [self.DEFAULT_OUTPUT_DIR, self.DEFAULT_VIDEO_OUTPUT_DIR, self.DEFAULT_PROFILE_OUTPUT_DIR, self.DEFAULT_IMAGE_DIR,
                        self.DEFAULT_IMAGE_OUTPUT_DIR, self.DEFAULT_IMAGE_SAMPLE_DIR]:
            if os.path.exists(chk_dir) is False:
                os.mkdir(chk_dir)

    def get_browser_type(self):
        result = DEFAULT_BROWSER_TYPE_FIREFOX
        test_name_list = self.test_method_name.split("_")
        if len(test_name_list) > 2:
            result = test_name_list[1].lower()
        return result



