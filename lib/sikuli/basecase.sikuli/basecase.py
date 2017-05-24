from sikuli import *  # NOQA
import json


class SikuliCase(object):
    """
    The base Sikuli case for Hasal.
    It will parse sys.argv, which is [library path for running cases, running statistics file path.

    After loading the stat file, it will prepare some default variables:
    - INPUT_LIB_PATH: the library path for running cases.
    - INPUT_STAT_FILE: the running statistics file, which is JSON format.
    - default_args: default input arguments, which is dict object.
    - INPUT_CASE_OUTPUT_NAME: the case output name, for example: test_firefox_foo_bar_<TIMESTAMP>
    - INPUT_ROOT_FOLDER: the Hasal root folder.
    - INPUT_TEST_TARGET: the test target URL address.
    - additional_args: additional input arguments, which is array list.

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

    def __init__(self, argv):
        self.argv = argv
        self.INPUT_LIB_PATH = argv[1]
        self.INPUT_STAT_FILE = argv[2]
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
