# coding=utf-8
import os
import sys
import copy
import time
import json
import platform
import unittest
import helper.desktopHelper as desktopHelper
import lib.helper.videoHelper as videoHelper
import lib.helper.targetHelper as targetHelper
import helper.generatorHelper as generatorHelper
from common.environment import Environment
from common.logConfig import get_logger
from common.windowController import WindowObject
from common.commonUtil import CommonUtil

logger = get_logger(__name__)


class BaseTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BaseTest, self).__init__(*args, **kwargs)

        # Init environment variables
        self.env = Environment(self._testMethodName, self._testMethodDoc)

        # Get current platform and its release version
        self.current_platform_name = sys.platform
        self.current_platform_ver = platform.release()

        # Get Terminal Window Object here when it still active
        if self.current_platform_name == 'darwin':
            terminal_title = ['Terminal.app', 'iTerm.app']
        elif self.current_platform_name == 'win32':
            terminal_title = ['cmd', 'Command Prompt', 'runtest.py']
        else:
            terminal_title = ['Hasal']

        # Linux will get current by wmctrl_get_current_window_id() method if current is True
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
        # check the video recording
        recording_enabled = CommonUtil.is_video_recording(self.firefox_config)

        if recording_enabled:
            for i in range(10):
                time.sleep(1)
                logger.debug("Check browser show up %d time(s)." % (i + 1))
                desktopHelper.lock_window_pos(self.browser_type)
                videoHelper.capture_screen(self.env, self.index_config, self.env.video_output_sample_1_fp,
                                           self.env.img_sample_dp,
                                           self.env.img_output_sample_1_fn)
                if desktopHelper.check_browser_show_up(self.env.img_sample_dp, self.env.img_output_sample_1_fn):
                    logger.debug("Browser shown, adjust viewport by setting.")
                    height_browser, width_browser = desktopHelper.adjust_viewport(self.browser_type,
                                                                                  self.env.img_sample_dp,
                                                                                  self.env.img_output_sample_1_fn)
                    height_offset = 0
                    terminal_width = width_browser
                    terminal_height = 60
                    if self.current_platform_name == 'linux2':
                        height_offset = 20
                        terminal_height = 60
                    elif self.current_platform_name == 'win32':
                        if self.current_platform_ver == '10':
                            logger.info("Move terminal window for Windows 10.")
                            height_offset = -4
                            terminal_height = 100
                        elif self.current_platform_ver == '7':
                            logger.info("Move terminal window for Windows 7.")
                            height_offset = 0
                            terminal_height = 80
                        else:
                            logger.info("Move terminal window for Windows.")
                            height_offset = 0
                            terminal_height = 80
                    elif self.current_platform_name == 'darwin':
                        # TODO: This offset settings only be tested on Mac Book Air
                        height_offset = 25
                        terminal_height = 80
                    terminal_x = 0
                    terminal_y = height_browser + height_offset
                    logger.info('Move Terminal to (X,Y,W,H): ({}, {}, {}, {})'.format(terminal_x,
                                                                                      terminal_y,
                                                                                      terminal_width,
                                                                                      terminal_height))
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

    def _platform_dep_settings_handler(self, config_value):
        if self.current_platform_name in config_value:
            if self.current_platform_ver in config_value[self.current_platform_name]:
                platform_dep_variables = copy.deepcopy(config_value[self.current_platform_name][self.current_platform_ver])
            else:
                platform_dep_variables = copy.deepcopy(config_value[self.current_platform_name][''])
            config_value.update(platform_dep_variables)
            return platform_dep_variables
        return {}

    def set_configs(self, config_variable_name, config_value):
        default_platform_dep_settings_key = "platform-dep-settings"
        if default_platform_dep_settings_key in config_value:
            # Load the index config's settings under "platform-dep-settings" base on platform
            platform_dep_variables = self._platform_dep_settings_handler(config_value[default_platform_dep_settings_key])
            config_value.update(platform_dep_variables)
            config_value.pop(default_platform_dep_settings_key)

        if hasattr(self, config_variable_name):
            # getattr is a way to get variable by reference and doesn't need to be set back
            getattr(self, config_variable_name).update(config_value)
        else:
            setattr(self, config_variable_name, config_value)

    def load_configs(self):
        config_fp_list = ['EXEC_CONFIG_FP', 'INDEX_CONFIG_FP', 'GLOBAL_CONFIG_FP', 'FIREFOX_CONFIG_FP', 'ONLINE_CONFIG_FP']

        for config_env_name in config_fp_list:
            config_variable_name = "_".join(config_env_name.split("_")[:2]).lower()
            with open(os.getenv(config_env_name)) as fh:
                config_value = json.load(fh)

            self.set_configs(config_variable_name, config_value)

    def setUp(self):

        # load all settings into self object
        self.load_configs()

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
        # TODO Maybe we can set runtime_case_data['browser_type' here, so baseTest.py can use one line self.browser_type = os.getenv("browser_type").

        if self.exec_config['user-simulation-tool'] == self.global_config['default-user-simulation-tool-webdriver']:
            self.browser_type = os.getenv("browser_type")
        else:
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
                generatorHelper.calculate(self.env, self.global_config, self.exec_config, self.index_config, self.firefox_config, self.online_config,
                                          os.getenv("SUITE_RESULT_DP"), self.crop_data)
            else:
                generatorHelper.calculate(self.env, self.global_config, self.exec_config, self.index_config, self.firefox_config, self.online_config,
                                          os.getenv("SUITE_RESULT_DP"))
        else:
            logger.warning("This running result of execution is not successful, return code: " + str(self.round_status))
