import os
import sys
from lib.common.commonUtil import StatusRecorder


class Sikuli():

    KEY_NAME_CURRENT_STATUS = 'current_status'
    KEY_NAME_SIKULI = 'sikuli'
    KEY_NAME_SIKULI_ARGS = 'args'
    KEY_NAME_SIKULI_ADDITIONAL_ARGS_LIST = 'additional_args'

    def __init__(self, run_sikulix_cmd_path, hasal_dir, running_statistics_file_path=''):
        self.run_sikulix_cmd_str = run_sikulix_cmd_path + " -r "
        self.hasal_dir = os.path.abspath(hasal_dir)
        self.running_statistics_file_path = os.path.abspath(running_statistics_file_path)
        self.status_recorder = None
        self._check_status_recorder()

    def set_syspath(self, hasal_dir):
        """
        Get the Sikuli Library folder path.
        @param hasal_dir: the Hasal root folder.
        @return: the `lib/sikuli` folder path under Hasal root folder.
        """
        library_path = os.path.join(hasal_dir, "lib", "sikuli")
        sys.path.append(library_path)
        return library_path

    def _check_status_recorder(self):
        self.status_recorder = StatusRecorder(self.running_statistics_file_path)
        self.status_recorder.record_current_status({})

    def _load_current_status(self):
        if self.status_recorder:
            return self.status_recorder.get_current_status()
        else:
            return {}

    def _load_sikuli_status(self):
        if self.status_recorder:
            current_status = self._load_current_status()
            return current_status.get(self.KEY_NAME_SIKULI, {})
        else:
            return {}

    def set_sikuli_status(self, key, value):
        """
        Set up the key, value pair into status file.
        @param key:
        @param value:
        @return:
        """
        if self.status_recorder:
            current_status = self._load_current_status()
            if self.KEY_NAME_SIKULI in current_status:
                current_status[self.KEY_NAME_SIKULI].update({key: value})
            else:
                current_status[self.KEY_NAME_SIKULI] = {}
                current_status[self.KEY_NAME_SIKULI].update({key: value})
            self.status_recorder.record_current_status(current_status)

    def run_test(self, script_name, case_output_name, test_target="", script_dp=None, args_list=[]):
        """

        @param script_name: <SIKULI_CASE_NAME>
        @param case_output_name: <CASE_NAME>_<TIMESTAMP>
        @param test_target: the target URL address.
        @param script_dp:  specify the Sikuli cases' folder path.
        @param args_list:
        @return:
        """
        if script_dp:
            script_dir_path = script_dp + os.sep + script_name + ".sikuli"
        else:
            script_path = os.path.join(self.hasal_dir, "tests")
            script_dir_path = script_path + os.sep + script_name + ".sikuli"

        default_args = {
            'case_output_name': str(case_output_name),
            'hasal_root_folder': self.hasal_dir,
            'stat_file_path': self.running_statistics_file_path
        }
        if test_target != "":
            default_args.update({'test_target': test_target})

        self.set_sikuli_status(self.KEY_NAME_SIKULI_ARGS, default_args)
        self.set_sikuli_status(self.KEY_NAME_SIKULI_ADDITIONAL_ARGS_LIST, args_list)

        args = [self.set_syspath(self.hasal_dir), self.running_statistics_file_path]

        return self.run_sikulix_cmd(script_dir_path, args)

    def run_sikulix_cmd(self, script_dir_path, args_list=[]):
        args_str = " ".join(['"{}"'.format(item) for item in args_list])
        cmd = self.run_sikulix_cmd_str + script_dir_path + " --args " + args_str
        return os.system(cmd)
