import os
import time
import platform
from ..helper.desktopHelper import DEFAULT_BROWSER_TYPE_FIREFOX


class Environment(object):

    DEFAULT_HASAL_DIR = os.getcwd()
    DEFAULT_THIRDPARTY_DIR = os.path.join(os.getcwd(), "thirdParty")
    DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "output")
    DEFAULT_VIDEO_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "videos")
    DEFAULT_PROFILE_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "profiles")
    DEFAULT_IMAGE_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images")
    DEFAULT_IMAGE_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images", "output")
    DEFAULT_IMAGE_SAMPLE_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images", "sample")
    DEFAULT_GECKO_PROFILER_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR, "geckoprofiler-signed.xpi")
    DEFAULT_CHROME_DRIVER_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR, "chromedriver")
    DEFAULT_SIKULI_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR)
    DEFAULT_TEST_RESULT = os.path.join(os.getcwd(), "result.json")

    DEFAULT_VIDEO_RECORDING_FPS = 90
    DEFAULT_VIDEO_RECORDING_POS_X = 72
    DEFAULT_VIDEO_RECORDING_POS_Y = 125
    DEFAULT_VIDEO_RECORDING_WIDTH = 1024
    DEFAULT_VIDEO_RECORDING_HEIGHT = 768

    DEFAULT_TEST_TARGET_FOLDER_URI = "0B6LePZQnd-uOTHhJNEhTN1pqYm8"
    if platform.system().lower() == "darwin":
        DEFAULT_VIDEO_RECORDING_DISPLAY = "1"
    else:
        DEFAULT_VIDEO_RECORDING_DISPLAY = ":0.0+" + str(DEFAULT_VIDEO_RECORDING_POS_X) + "," + str(
            DEFAULT_VIDEO_RECORDING_POS_X)
    DEFAULT_VIDEO_RECORDING_CODEC = "h264_fast"

    def __init__(self, test_method_name):
        self.time_stamp = str(int(time.time()))
        self.test_method_name = test_method_name
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



