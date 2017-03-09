import os
import sys
import time
import json
import unittest
import helper.desktopHelper as desktopHelper
import lib.helper.videoHelper as videoHelper
import lib.helper.targetHelper as targetHelper
import helper.resultHelper as resultHelper
from common.environment import Environment
from common.logConfig import get_logger
from ..common.windowController import WindowObject

logger = get_logger(__name__)


class BaseTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BaseTest, self).__init__(*args, **kwargs)

        # Init environment variables
        self.env = Environment(self._testMethodName, self._testMethodDoc)
        # TODO get Terminal Window Object here when it still active
        if sys.platform == 'darwin':
            terminal_title = ['Terminal.app', 'iTerm.app']
        elif sys.platform == 'win32':
            terminal_title = ['cmd']
        elif sys.platform == 'linux2':
            terminal_title = ['Hasal']
        self.terminal_window_obj = WindowObject(terminal_title, current=True)

    def set_profiler_path(self):
        for name in self.env.firefox_settings_extensions:
            if not name.startswith("chrome"):
                self.env.firefox_settings_extensions[name]['path'] = "lib.profiler." + name[0].lower() + name[1:]

    def set_variable(self, **kwargs):
        for variable_name in kwargs.keys():
            setattr(self, variable_name, kwargs[variable_name])

    def args_parser(self, input_script_name, input_args):
        result_args = []
        for arg in input_args:
            if type(arg) == dict:
                if "clone_url" in arg.keys():
                    test_url_id = getattr(self.env, arg["clone_url"])
                    self.test_url, self.test_url_id = \
                        self.target_helper.clone_target(test_url_id, input_script_name + "_" + self.env.time_stamp)
                    result_args.append(arg["clone_url"])
                else:
                    result_args.append(arg[arg.keys()[0]])
            else:
                result_args = input_args
        return result_args

    def get_browser_done(self):
        if self.env.PROFILER_FLAG_AVCONV in self.env.firefox_settings_extensions:
            if self.env.firefox_settings_extensions[self.env.PROFILER_FLAG_AVCONV]['enable'] is True:
                for i in range(10):
                    time.sleep(1)
                    logger.debug("Check browser show up %d time(s)." % (i + 1))
                    desktopHelper.lock_window_pos(self.browser_type)
                    videoHelper.capture_screen(self.env, self.env.video_output_sample_1_fp, self.env.img_sample_dp,
                                               self.env.img_output_sample_1_fn)
                    if desktopHelper.check_browser_show_up(self.env.img_sample_dp, self.env.img_output_sample_1_fn):
                        logger.debug("Browser shown, adjust viewport by setting.")
                        height_adjustment, width_adjustment = desktopHelper.adjust_viewport(self.browser_type,
                                                                                            self.env.img_sample_dp,
                                                                                            self.env.img_output_sample_1_fn)
                        # TODO
                        terminal_x = 0
                        terminal_y = height_adjustment
                        terminal_width = 120
                        terminal_height = 20
                        self.terminal_window_obj.move_window_pos(pos_x=terminal_x,
                                                                 pos_y=terminal_y,
                                                                 window_width=terminal_width,
                                                                 window_height=terminal_height)
                        break
        else:
            time.sleep(3)
            desktopHelper.lock_window_pos(self.browser_type)

    def clone_test_file(self):
        if hasattr(self, "test_target"):
            if hasattr(self, "target_folder"):
                self.test_url, self.test_url_id = self.target_helper.clone_target(self.test_target,
                                                                                  self.env.output_name,
                                                                                  self.target_folder)
                logger.info("The test url after cloned is : [%s]" % self.test_url)
            else:
                self.test_url, self.test_url_id = self.target_helper.clone_target(self.test_target,
                                                                                  self.env.output_name)
                logger.info("The test url after cloned is : [%s]" % self.test_url)

    def remove_test_file(self):
        if hasattr(self, "test_url_id"):
            self.target_helper.delete_target(self.test_url_id)

    def setUp(self):
        # Original profiler list was substitute by self.env.firefox_settings_extensions
        # We set the original profiler path variable in the variable
        self.set_profiler_path()

        # init target helper
        self.target_helper = targetHelper.TagetHelper(self.env)

        # Init sikuli status for webdriver/sikuli
        self.round_status = 0

        # Init output dirs
        self.env.init_output_dir()

        # get browser type
        self.browser_type = self.env.get_browser_type()

        # clone test target
        self.clone_test_file()

    def tearDown(self):
        # Delete Url
        self.remove_test_file()

        # output status to static file
        with open(self.env.DEFAULT_STAT_RESULT, "w") as fh:
            stat_data = {'round_status': str(self.round_status)}
            json.dump(stat_data, fh)

        # output result
        if self.round_status == 0:
            if hasattr(self, "crop_data"):
                resultHelper.result_calculation(self.env, self.crop_data,
                                                int(os.getenv("CALC_SI")), int(os.getenv("ENABLE_WAVEFORM")),
                                                os.getenv("PERFHERDER_REVISION"), os.getenv("PERFHERDER_PKG_PLATFORM"),
                                                os.getenv("SUITE_UPLOAD_DP"))
            else:
                resultHelper.result_calculation(self.env, calc_si=int(os.getenv("CALC_SI")),
                                                waveform=int(os.getenv("ENABLE_WAVEFORM")),
                                                revision=os.getenv("PERFHERDER_REVISION"),
                                                pkg_platform=os.getenv("PERFHERDER_PKG_PLATFORM"),
                                                suite_upload_dp=os.getenv("SUITE_UPLOAD_DP"))
        else:
            logger.warning("This running result of sikuli execution is not successful, return code: " + str(self.round_status))
