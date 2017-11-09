import os
import json
import baseTest
import pyperclip
import helper.desktopHelper as desktopHelper
import lib.sikuli as sikuli
from helper.profilerHelper import Profilers
from common.logConfig import get_logger
from common.commonUtil import StatusRecorder
from common.statusFileCreator import StatusFileCreator

logger = get_logger(__name__)


class SpeedometerBaseTest(baseTest.BaseTest):

    def __init__(self, *args, **kwargs):
        super(SpeedometerBaseTest, self).__init__(*args, **kwargs)

    def output_speedometer_result(self):
        data = pyperclip.paste()
        iteration_detail_list = [filter(None, line.split(" "))[-2].split("\t")[-1] for line in data.splitlines() if len(line.split(" ")) >= 3 and "Iteration" in line.split(" ")]
        mean_value = float([line.split(" ")[1].split(":")[1] for line in data.splitlines() if len(line.split(" ")) == 5 and "Arithmetic" in line.split(" ")][0])
        deviation_value = float([line.split(" ")[3] for line in data.splitlines() if len(line.split(" ")) == 5 and "Arithmetic" in line.split(" ")][0])
        output_result_fp = os.path.join(os.getenv("SUITE_RESULT_DP"), "result.json")
        reulst_data = {"iteration_detail": iteration_detail_list, "mean_value": mean_value, "deviation_value": deviation_value, "raw_data": data}
        with open(output_result_fp, "wb") as fh:
            json.dump(reulst_data, fh, indent=2)

    def setUp(self):
        super(SpeedometerBaseTest, self).setUp()

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

        # launch browser
        _, self.profile_dir_path = desktopHelper.launch_browser(self.browser_type, env=self.env,
                                                                profiler_list=self.env.firefox_settings_extensions,
                                                                exec_config=self.exec_config,
                                                                firefox_config=self.firefox_config,
                                                                chrome_config=self.chrome_config)
        # wait browser ready
        self.get_browser_done()

    def tearDown(self):

        # Stop profiler and save profile data
        self.profilers.stop_profiling(self.profile_dir_path)

        # Stop browser
        if self.exec_config['keep-browser'] is False:
            desktopHelper.close_browser(self.browser_type)

        # output clipboard to result.json
        if self.round_status == 0:
            # fill normal status into running_statistics.json
            self.objStatusRecorder = StatusRecorder(self.global_config['default-running-statistics-fn'])
            self.objStatusRecorder.record_current_status({self.objStatusRecorder.STATUS_SIKULI_RUNNING_VALIDATION: str(self.round_status)})
            self.objStatusRecorder.record_current_status({self.objStatusRecorder.STATUS_FPS_VALIDATION: 0})
            self.objStatusRecorder.record_current_status({self.objStatusRecorder.STATUS_IMG_COMPARE_RESULT: self.objStatusRecorder.PASS_IMG_COMPARE_RESULT})

            # output result
            self.output_speedometer_result()

        # write sikuli status into status file
        if self.status_job_id_path:
            StatusFileCreator.create_status_file(self.status_job_id_path, StatusFileCreator.STATUS_TAG_RUNTEST_CMD, 300, {"round_status": self.round_status})
