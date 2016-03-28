__author__ = 'shako'
import unittest
from selenium import webdriver
from videoUtilHelper import RecordingVideoObj
from videoUtilHelper import VideoAnalyzeObj
from selenium.webdriver.common.keys import Keys
import json
import time
import io
import os

DEFAULT_THIRDPARTY_DIR = os.path.join(os.getcwd(), "thirdParty")
DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "output")
DEFAULT_VIDEO_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "videos")
DEFAULT_PROFILE_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "profiles")
DEFAULT_IMAGE_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images")
DEFAULT_IMAGE_OUTPUT_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images", "output")
DEFAULT_IMAGE_SAMPLE_DIR = os.path.join(DEFAULT_OUTPUT_DIR, "images", "sample")

DEFAULT_GECKO_PROFILER_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR, "geckoprofiler-signed.xpi")
DEFAULT_CHROME_DRIVER_PATH = os.path.join(DEFAULT_THIRDPARTY_DIR, "chromedriver")

DEFAULT_TEST_RESULT = os.path.join(os.getcwd(), "result.json")

DEFAULT_BROWSER_POS_X = 0
DEFAULT_BROWSER_POS_Y = 0
DEFAULT_BROWSER_WIDTH = 1200
DEFAULT_BROWSER_HEIGHT = 980

DEFAULT_BROWSER_TYPE_FIREFOX = "firefox"
DEFAULT_BROWSER_TYPE_CHROME = "chrome"


class PerfBaseTest(unittest.TestCase):

    video_recording_obj = None
    driver = None

    def initOutputDir(self):
        # Init output folder
        for chk_dir in [DEFAULT_OUTPUT_DIR, DEFAULT_VIDEO_OUTPUT_DIR, DEFAULT_PROFILE_OUTPUT_DIR, DEFAULT_IMAGE_DIR,
                        DEFAULT_IMAGE_OUTPUT_DIR, DEFAULT_IMAGE_SAMPLE_DIR]:
            if os.path.exists(chk_dir) is False:
                os.mkdir(chk_dir)

    def initOutputFn(self):
        # Init output file name
        self.output_name = self._testMethodName + "_" + str(int(time.time()))
        self.video_output_fp = os.path.join(DEFAULT_VIDEO_OUTPUT_DIR, self.output_name + ".mkv")
        self.video_output_sample_1_fp = os.path.join(DEFAULT_VIDEO_OUTPUT_DIR, self.output_name + "_sample_1.mkv")
        self.video_output_sample_2_fp = os.path.join(DEFAULT_VIDEO_OUTPUT_DIR, self.output_name + "_sample_2.mkv")
        self.img_sample_dp = os.path.join(DEFAULT_IMAGE_SAMPLE_DIR, self.output_name)
        self.img_output_dp = os.path.join(DEFAULT_IMAGE_OUTPUT_DIR, self.output_name)
        self.img_output_sample_1_fn = self.output_name + "_sample_1.jpg"
        self.img_output_sample_2_fn = self.output_name + "_sample_2.jpg"
        self.profile_timing_json_fp = os.path.join(DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + "_timing.json")
        self.profile_timing_bin_fp = os.path.join(DEFAULT_PROFILE_OUTPUT_DIR, self.output_name + ".bin")

    def initWebDriver(self):
        self.browser_type = DEFAULT_BROWSER_TYPE_FIREFOX
        test_name_list = self._testMethodName.split("_")
        if len(test_name_list) > 2:
            self.browser_type = test_name_list[1].lower()
        if self.browser_type == DEFAULT_BROWSER_TYPE_CHROME:
            self.driver = webdriver.Chrome(DEFAULT_CHROME_DRIVER_PATH)
        else:
            # The profiler starts automatically
            # Install gecko profiler addon
            # Ref: https://github.com/bgirard/Gecko-Profiler-Addon
            fp = webdriver.FirefoxProfile()
            fp.add_extension(extension=DEFAULT_GECKO_PROFILER_PATH)
            self.driver = webdriver.Firefox(firefox_profile=fp)

    def setUp(self):
        # Init output folder
        self.initOutputDir()

        # Init output file name
        self.initOutputFn()

        # Start video recording
        # TODO: Extract the framerate as a variable?
        self.video_recording_obj = RecordingVideoObj()
        self.video_recording_obj.start_video_recording(self.video_output_fp)

        # init webdriver based on your test method name
        self.initWebDriver()

        # move the browser window to the top left position
        self.driver.set_window_position(DEFAULT_BROWSER_POS_X, DEFAULT_BROWSER_POS_Y)
        self.driver.set_window_size(DEFAULT_BROWSER_WIDTH, DEFAULT_BROWSER_HEIGHT)

    def tearDown(self):
        # Stop video recording
        self.video_recording_obj.stop_video_recording()

        if self.browser_type == DEFAULT_BROWSER_TYPE_FIREFOX:
            # Stop gecko profiler recording
            self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.SHIFT + '2')

            time.sleep(10) #XXX: Change this to active wait

            # Switch to the cleopetra.io tab
            main_window = self.driver.current_window_handle
            self.driver.switch_to_window(main_window) # Switch to current frame

            self.driver.set_script_timeout(5)
            recording = self.driver.execute_async_script(
                "var done = arguments[0];" +
                "console.log(done);" +
                "window.Parser.getSerializedProfile(true, function (serializedProfile) {" +
                "  done(serializedProfile);"
                "});"
            )

            # dump profile to .bin file
            with io.open(self.profile_timing_bin_fp, 'w', encoding='utf-8') as f:
                f.write(recording)

        self.driver.close()

        # analyze the video with sample image
        video_analyze_obj = VideoAnalyzeObj()
        self.outputResult(video_analyze_obj.run_analyze(self.video_output_fp, self.img_output_dp, self.img_sample_dp))

    def dumpToJson(self, output_data, output_fp, mode="wb"):
        with open(output_fp, mode) as fh:
            json.dump(output_data, fh, indent=2)

    def outputResult(self, current_run_result):
        #result = {'class_name': {'total_run_no': 0, 'error_no': 0, 'total_time': 0, 'avg_time': 0, 'max_time': 0, 'min_time': 0, 'detail': []}}
        run_time = 0
        if os.path.exists(DEFAULT_TEST_RESULT):
            with open(DEFAULT_TEST_RESULT) as fh:
                result = json.load(fh)
        else:
            result = {}

        if len(current_run_result) == 2:
            run_time = current_run_result[0]['time_seq'] - current_run_result[1]['time_seq']

        if self._testMethodName in result:
            result[self._testMethodName]['total_run_no'] += 1
            result[self._testMethodName]['total_time'] += run_time
            if run_time == 0:
                result[self._testMethodName]['error_no'] += 1
            if (result[self._testMethodName]['total_run_no'] - result[self._testMethodName]['error_no']) == 0:
                result[self._testMethodName]['avg_time'] = 0
            else:
                result[self._testMethodName]['avg_time'] = result[self._testMethodName]['total_time'] / (result[self._testMethodName]['total_run_no'] - result[self._testMethodName]['error_no'])
            if run_time > result[self._testMethodName]['max_time']:
                result[self._testMethodName]['max_time'] = run_time
            if run_time < result[self._testMethodName]['min_time']:
                result[self._testMethodName]['min_time'] = run_time
            result[self._testMethodName]['detail'].extend(current_run_result)
        else:
            result[self._testMethodName] = {}
            result[self._testMethodName]['total_run_no'] = 1
            result[self._testMethodName]['total_time'] = run_time
            if run_time == 0:
                result[self._testMethodName]['error_no'] = 1
                result[self._testMethodName]['avg_time'] = 0
                result[self._testMethodName]['max_time'] = 0
                result[self._testMethodName]['min_time'] = 0
            else:
                result[self._testMethodName]['error_no'] = 0
                result[self._testMethodName]['avg_time'] = run_time
                result[self._testMethodName]['max_time'] = run_time
                result[self._testMethodName]['min_time'] = run_time
            result[self._testMethodName]['detail'] = current_run_result

        self.dumpToJson(result, DEFAULT_TEST_RESULT)





