from sikuli import *  # NOQA
import json
import common


class SikuliCase(object):
    """
    The base Sikuli case for Hasal.
    It will parse sys.argv, which is [library path for running cases, running statistics file path.

    After loading the stat file, it will prepare some default variables:
    - operating_system: The operating system type. It will be one of following string: MAC, LINUX, WINDOWS, NOT_SUPPORTED.
    - operating_system_version: The operating system version.
    - common: The common General object, which contains some useful methods.
    - INPUT_LIB_PATH: The library path for running cases.
    - INPUT_STAT_FILE: The running statistics file, which is JSON format.
    - default_args: The default input arguments, which is dict object.
    - INPUT_CASE_OUTPUT_NAME: The case output name, for example: test_firefox_foo_bar_<TIMESTAMP>
    - INPUT_ROOT_FOLDER: The Hasal root folder.
    - INPUT_TEST_TARGET: The test target URL address.
    - additional_args: The additional input arguments, which is array list.

    Usage:
    ```python
        INPUT_LIB_PATH = sys.argv[1]
        sys.path.append(INPUT_LIB_PATH)
        import common
        import basecase

        class MyCase(basecase.SikuliCase):
            def run(self):
                print('Thank you 9527.')

        case = MyCase(sys.argv)
        case.run()
    ```

    """
    KEY_NAME_CURRENT_STATUS = 'current_status'
    KEY_NAME_SIKULI = 'sikuli'
    KEY_NAME_SIKULI_ARGS = 'args'
    KEY_NAME_SIKULI_ADDITIONAL_ARGS_LIST = 'additional_args'

    # for loading region settings
    KEY_REGION = 'region'
    # for writing region settings
    KEY_REGION_OVERRIDE = 'region_override'

    def __init__(self, argv):
        # loading default argv
        self.argv = argv
        self.INPUT_LIB_PATH = argv[1]
        self.INPUT_STAT_FILE = argv[2]

        # Env.getOS() will return one of following object, OS.MAC, OS.LINUX, OS.WINDOWS, and OS.NOT_SUPPORTED.
        self.operating_system = Env.getOS()
        self.operating_system_version = Env.getOSVersion()

        # loading general common object
        self.common = common.General()
        self._web_page = common.WebApp()

        # loading other settings
        self._load_stat_json()
        self._load_addtional_args()

    def _load_stat_json(self):
        with open(self.INPUT_STAT_FILE, 'r') as stat_fh:
            status = json.load(stat_fh)

        self.current_status = status.get(self.KEY_NAME_CURRENT_STATUS, {})
        self.sikuli_status = self.current_status.get(self.KEY_NAME_SIKULI, {})
        self.default_args = self.sikuli_status.get(self.KEY_NAME_SIKULI_ARGS, {})

        self.INPUT_CASE_OUTPUT_NAME = self.default_args.get('case_output_name', '')
        self.INPUT_ROOT_FOLDER = self.default_args.get('hasal_root_folder', '')
        self.INPUT_TEST_TARGET = self.default_args.get('test_target', '')

        self.additional_args = self.sikuli_status.get(self.KEY_NAME_SIKULI_ADDITIONAL_ARGS_LIST, [])
        # reset the data of Override Region
        self.append_to_stat_json(self.KEY_REGION_OVERRIDE, {})

    def find_match_region(self, component, similarity=0.70, timeout=10):
        """
        Find the matched region object base on component. Default timeout is 10 sec.
        @param component: Specify the wait component, which is an array of [Sikuli pattern, offset-x, offset-y].
        @param timeout: Wait timeout second, the min timeout is 1 sec. Default is 10 sec.
        @param similarity: The pattern comparing similarity, from 0 to 1. Default is 0.70.
        @return:The matched region object.
        """
        _, match_obj = self._web_page._wait_for_loaded(component=component, similarity=similarity, timeout=timeout)
        return match_obj

    def append_to_stat_json(self, key, value):
        """
        Append key-value pair into stat JSON file under "current_status/sikuli" path.
        @param key: The key name.
        @param value: value.
        """
        with open(self.INPUT_STAT_FILE, 'r') as stat_fh:
            status = json.load(stat_fh)
            current_status = status.get(self.KEY_NAME_CURRENT_STATUS, {})
            sikuli_status = current_status.get(self.KEY_NAME_SIKULI, {})
            sikuli_status[key] = value
        with open(self.INPUT_STAT_FILE, 'w') as stat_fh:
            json.dump(status, stat_fh)

    def _load_addtional_args(self):
        pass

    def set_override_region_settings(self, customized_region_name, sikuli_region_obj):
        """
        Set the region information from Sikuli case into Stat File.
        It will append the Sikuli Region Object's x, y, w, h information for cropping images.
        @param customized_region_name: the customized region name, which be defined in index-config file.
        @param sikuli_region_obj: The Sikuli Region object. ex: find(Pattern('foo.png'))
        @return:
        """
        region_dict = self.sikuli_status.get(self.KEY_REGION, {})
        if customized_region_name in region_dict:
            customized_region_dict = region_dict[customized_region_name]

            customized_region_dict['x'] = sikuli_region_obj.x
            customized_region_dict['y'] = sikuli_region_obj.y
            customized_region_dict['w'] = sikuli_region_obj.w
            customized_region_dict['h'] = sikuli_region_obj.h
            customized_region = {
                customized_region_name: customized_region_dict
            }
            self.append_to_stat_json(self.KEY_REGION_OVERRIDE, customized_region)
            print('[INFO] Found [{r_name}] with [x,y,w,h]: [{x},{y},{w},{h}]'.format(r_name=customized_region_name,
                                                                                     x=sikuli_region_obj.x,
                                                                                     y=sikuli_region_obj.y,
                                                                                     w=sikuli_region_obj.w,
                                                                                     h=sikuli_region_obj.h))
            return True
        else:
            print('[ERROR] Cannot find the settings [{r_name}] of Customized Region from index-config.'.format(r_name=customized_region_name))
            return False

    def run(self):
        """
        Implement the case steps by override this method.
        """
        raise NotImplementedError()


class SikuliInputLatencyCase(SikuliCase):
    """
    The base Sikuli case for Input Latency cases.

    It will loading more additional arguments:
    - INPUT_IMG_SAMPLE_DIR_PATH = self.additional_args[0]
    - INPUT_IMG_OUTPUT_SAMPLE_1_NAME = self.additional_args[1]
    - INPUT_RECORD_WIDTH = self.additional_args[2]
    - INPUT_RECORD_HEIGHT = self.additional_args[3]
    - INPUT_TIMESTAMP_FILE_PATH = self.additional_args[4]
    """
    def _load_addtional_args(self):
        self.INPUT_IMG_SAMPLE_DIR_PATH = self.additional_args[0]
        self.INPUT_IMG_OUTPUT_SAMPLE_1_NAME = self.additional_args[1]
        self.INPUT_RECORD_WIDTH = self.additional_args[2]
        self.INPUT_RECORD_HEIGHT = self.additional_args[3]
        self.INPUT_TIMESTAMP_FILE_PATH = self.additional_args[4]


class SikuliRunTimeCase(SikuliCase):
    """
    The base Sikuli case for Run Time cases.
    """
