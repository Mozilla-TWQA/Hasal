import time
import json
import baseTest
import helper.desktopHelper as desktopHelper
import lib.sikuli as sikuli
import lib.helper.videoHelper as videoHelper
from helper.profilerHelper import Profilers
from common.logConfig import get_logger
from common.commonUtil import CommonUtil
from common.commonUtil import StatusRecorder

logger = get_logger(__name__)


class PerfBaseTest(baseTest.BaseTest):

    def __init__(self, *args, **kwargs):
        super(PerfBaseTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(PerfBaseTest, self).setUp()

        # init sikuli
        self.sikuli = sikuli.Sikuli(self.env.run_sikulix_cmd_path, self.env.hasal_dir,
                                    running_statistics_file_path=self.global_config['default-running-statistics-fn'])
        # set up the Customized Region settings
        if StatusRecorder.SIKULI_KEY_REGION in self.index_config:
            logger.info('Set Sikuli Status for Customized Region')
            self.sikuli.set_sikuli_status(StatusRecorder.SIKULI_KEY_REGION, self.index_config[StatusRecorder.SIKULI_KEY_REGION])

        # Start video recordings
        self.profilers = Profilers(self.env, self.index_config, self.exec_config, self.browser_type, self.sikuli)
        self.profilers.start_profiling(self.env.firefox_settings_extensions)

        # Record initial timestamp
        with open(self.env.DEFAULT_TIMESTAMP, "w") as fh:
            timestamp = {self.env.INITIAL_TIMESTAMP_NAME: str(time.time())}
            json.dump(timestamp, fh)

        # launch browser
        _, self.profile_dir_path = desktopHelper.launch_browser(self.browser_type, env=self.env,
                                                                profiler_list=self.env.firefox_settings_extensions,
                                                                exec_config=self.exec_config)

        # wait browser ready
        self.get_browser_done()

        # capture 1st snapshot
        time.sleep(5)

        # check the video recording
        recording_enabled = CommonUtil.is_video_recording(self.firefox_config)
        if recording_enabled and self.index_config.get('snapshot-base-sample1', False) is True:
            videoHelper.capture_screen(self.env, self.index_config, self.exec_config,
                                       self.env.video_output_sample_1_fp,
                                       self.env.img_sample_dp,
                                       self.env.img_output_sample_1_fn)
        time.sleep(2)

        # Record timestamp t1
        with open(self.env.DEFAULT_TIMESTAMP, "r+") as fh:
            timestamp = json.load(fh)
            timestamp['t1'] = time.time()
            fh.seek(0)
            fh.write(json.dumps(timestamp))

    def tearDown(self):

        # Record timestamp t2
        with open(self.env.DEFAULT_TIMESTAMP, "r+") as fh:
            timestamp = json.load(fh)
            if 't2' not in timestamp:
                timestamp['t2'] = time.time()
                fh.seek(0)
                fh.write(json.dumps(timestamp))

        # capture 2nd snapshot
        time.sleep(5)

        recording_enabled = CommonUtil.is_video_recording(self.firefox_config)
        if recording_enabled and self.index_config.get('snapshot-base-sample2', False) is True:
            videoHelper.capture_screen(self.env, self.index_config, self.exec_config,
                                       self.env.video_output_sample_2_fp,
                                       self.env.img_sample_dp,
                                       self.env.img_output_sample_2_fn)

        # Stop profiler and save profile data
        self.profilers.stop_profiling(self.profile_dir_path)

        # Stop browser
        if self.exec_config['keep-browser'] is False:
            desktopHelper.close_browser(self.browser_type)

        super(PerfBaseTest, self).tearDown()
