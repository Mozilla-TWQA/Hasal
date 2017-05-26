# coding=utf-8
import os
import sys
import copy
import time
import json
import platform
import unittest
import helper.desktopHelper as desktopHelper
import helper.terminalHelper as terminalHelper
import lib.helper.videoHelper as videoHelper
import lib.helper.targetHelper as targetHelper
import helper.generatorHelper as generatorHelper
from common.environment import Environment
from common.logConfig import get_logger
from common.commonUtil import CommonUtil
from common.commonUtil import StatusRecorder
from common.visualmetricsWrapper import find_image_viewport

logger = get_logger(__name__)


class BaseTest(unittest.TestCase):
    class ConfigName(object):
        EXEC = 'exec_config'
        INDEX = 'index_config'
        GLOBAL = 'global_config'
        FIREFOX = 'firefox_config'
        ONLINE = 'online_config'

    def __init__(self, *args, **kwargs):
        super(BaseTest, self).__init__(*args, **kwargs)

        # Init config name inner class
        self.config_name = self.ConfigName()

        # Init environment variables
        self.env = Environment(self._testMethodName, self._testMethodDoc)

        # Get current platform and its release version
        self.current_platform_name = sys.platform
        self.current_platform_ver = platform.release()

        # load all settings into self object
        self.load_configs()

        # Get Terminal Window Object
        self.terminal_window_obj = terminalHelper.get_terminal_window_object()

    def set_profiler_path(self):
        for name in self.env.firefox_settings_extensions:
            if not name.lower().startswith("chrome"):
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
            viewport = dict()
            viewport_ref_fp = os.path.join(self.env.img_sample_dp, self.env.img_output_sample_1_fn)
            is_expected_viewport = False
            desktopHelper.lock_window_pos(self.browser_type, self.exec_config)
            for i in range(25):
                time.sleep(1)
                videoHelper.capture_screen(self.env, self.index_config, self.exec_config,
                                           self.env.video_output_sample_1_fp,
                                           self.env.img_sample_dp,
                                           self.env.img_output_sample_1_fn)
                viewport = find_image_viewport(viewport_ref_fp)
                if desktopHelper.is_above_half_viewport(viewport, self.exec_config):
                    logger.debug("Browser shown, adjust viewport by setting %d time(s)." % (i + 1))
                    height_browser, width_browser = desktopHelper.adjust_viewport(self.browser_type,
                                                                                  viewport,
                                                                                  self.exec_config)
                    # get the terminal location
                    terminal_location = terminalHelper.get_terminal_location(0, 0, width_browser, height_browser)
                    terminal_x = terminal_location.get('x', 0)
                    terminal_y = terminal_location.get('y', 0)
                    terminal_width = terminal_location.get('width', 0)
                    terminal_height = terminal_location.get('height', 0)

                    logger.info('Move Terminal to (X,Y,W,H): ({}, {}, {}, {})'.format(terminal_x,
                                                                                      terminal_y,
                                                                                      terminal_width,
                                                                                      terminal_height))
                    self.terminal_window_obj.move_window_pos(pos_x=terminal_x,
                                                             pos_y=terminal_y,
                                                             window_width=terminal_width,
                                                             window_height=terminal_height)
                    is_expected_viewport = desktopHelper.is_expected_viewport(viewport, self.exec_config)
                    if is_expected_viewport:
                        break
                else:
                    logger.info("Browser launched but viewport still less than half size, already wait %d second(s)." % (i + 1))
            # TODO: Doesn't support runtime viewport adjustment for linux now thus won't verify expected viewport size
            if not is_expected_viewport and self.current_platform_name != 'linux2':
                raise Exception('[ERROR] Viewport size is not expected: {}'.format(viewport))
        else:
            time.sleep(3)
            desktopHelper.lock_window_pos(self.browser_type, self.exec_config)

    def clone_test_file(self):
        if hasattr(self, "test_target"):
            # init target helper
            self.target_helper = targetHelper.TagetHelper(self.env, self.global_config)
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

    # be careful to have "default" value for each and every platform in conf file, or it would raise exception.
    def extract_platform_dep_settings(self, config_value):
        platform_dep_variables = {}
        # get current platform value or default value of it
        if self.current_platform_name in config_value:
            if self.current_platform_ver in config_value[self.current_platform_name]:
                platform_dep_variables = copy.deepcopy(config_value[self.current_platform_name][self.current_platform_ver])
            elif 'default' in config_value[self.current_platform_name]:
                platform_dep_variables = copy.deepcopy(config_value[self.current_platform_name]['default'])

        # return {} if no matching system platform and no default value
        return platform_dep_variables

    # This will set new configs into variables and update if the variables already exist
    def set_configs(self, config_variable_name, config_value):
        # only the config in the following list can be created or updated
        acceptable_config_list = [self.config_name.EXEC, self.config_name.INDEX, self.config_name.GLOBAL,
                                  self.config_name.FIREFOX, self.config_name.ONLINE]
        if config_variable_name not in acceptable_config_list:
            raise Exception('Invalid configuration name {config_name}: {config_value}'
                            .format(config_name=config_variable_name, config_value=config_value))

        default_platform_dep_settings_key = "platform-dep-settings"
        if default_platform_dep_settings_key in config_value:
            # Load the index config's settings under "platform-dep-settings" base on platform
            platform_dep_variables = self.extract_platform_dep_settings(config_value[default_platform_dep_settings_key])
            config_value.update(platform_dep_variables)
            config_value.pop(default_platform_dep_settings_key)

        if hasattr(self, config_variable_name):
            # getattr is a way to get variable by reference and doesn't need to be set back
            new_config_value = getattr(self, config_variable_name)
            new_config_value.update(config_value)
            setattr(self, config_variable_name, new_config_value)
        else:
            setattr(self, config_variable_name, config_value)

    def load_configs(self):
        config_fp_list = ['EXEC_CONFIG_FP', 'INDEX_CONFIG_FP', 'GLOBAL_CONFIG_FP',
                          'FIREFOX_CONFIG_FP', 'ONLINE_CONFIG_FP']

        for config_env_name in config_fp_list:
            config_variable_name = config_env_name.rsplit('_', 1)[0].lower()
            with open(os.getenv(config_env_name)) as fh:
                config_value = json.load(fh)

            self.set_configs(config_variable_name, config_value)
        self.extract_screen_settings_from_env()

    # TODO: these screen settings should be moved to exec config in the future
    def extract_screen_settings_from_env(self):
        screen_settings = {
            'browser-pos-x': self.env.DEFAULT_BROWSER_POS_X,
            'browser-pos-y': self.env.DEFAULT_BROWSER_POS_Y,
            'browser-width': self.env.DEFAULT_BROWSER_WIDTH,
            'browser-height': self.env.DEFAULT_BROWSER_HEIGHT,
            'viewport-width': self.env.DEFAULT_VIEWPORT_WIDTH,
            'viewport-height': self.env.DEFAULT_VIEWPORT_HEIGHT,
            'video-recording-pos-x': self.env.DEFAULT_VIDEO_RECORDING_POS_X,
            'video-recording-pos-y': self.env.DEFAULT_VIDEO_RECORDING_POS_Y,
            'video-recording-width': self.env.DEFAULT_VIDEO_RECORDING_WIDTH,
            'video-recording-height': self.env.DEFAULT_VIDEO_RECORDING_HEIGHT
        }
        self.set_configs(self.config_name.EXEC, screen_settings)

    def get_new_recording_size(self):
        recording_width = min(self.exec_config['browser-width'] + 100, 1920)
        if self.current_platform_name.lower() == "darwin":
            recording_height = min(self.exec_config['browser-height'] + 120, 900)
        else:
            recording_height = min(self.exec_config['browser-height'] + 180, 1080)
        recording_setting = {'video-recording-width': recording_width,
                             'video-recording-height': recording_height
                             }
        return recording_setting

    def setUp(self):

        # Original profiler list was substitute by self.env.firefox_settings_extensions
        # We set the original profiler path variable in the variable
        self.set_profiler_path()

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
        self.objStatusRecorder = StatusRecorder(self.global_config['default-running-statistics-fn'])
        self.objStatusRecorder.record_current_status({self.objStatusRecorder.STATUS_SIKULI_RUNNING_VALIDATION: str(self.round_status)})

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
