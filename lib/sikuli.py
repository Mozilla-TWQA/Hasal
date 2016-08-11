import os
import sys


class Sikuli():

    def __init__(self, run_sikulix_cmd_path, hasal_dir):
        self.run_sikulix_cmd_str = run_sikulix_cmd_path + " -r "
        self.hasal_dir = hasal_dir

    # hasal_dir:  DEFAULT_HASAL_DIR in environment.py
    def set_syspath(self, hasal_dir):
        library_path = os.path.join(hasal_dir, "lib", "sikuli")
        sys.path.append(library_path)
        return library_path

    # test_name:  test_(browser)_(test_name)
    # timestamp:  please pass in the integer generated from main python for folder record
    def run_test(self, script_name, timestamp="0000000000", test_target="", script_dp=None):
        if script_dp:
            script_dir_path = script_dp + os.sep + script_name + ".sikuli"
        else:
            script_path = os.path.join(self.hasal_dir, "tests")
            script_dir_path = script_path + "/" + script_name + ".sikuli"
        args_list = [str(timestamp), self.set_syspath(self.hasal_dir)]
        if test_target != "":
            args_list.append(test_target)
        return self.run_sikulix_cmd(script_dir_path, args_list)

    def run_sikulix_cmd(self, script_dir_path, args_list=[]):
        args_str = " ".join(args_list)
        cmd = self.run_sikulix_cmd_str + script_dir_path + " --args " + args_str
        return os.system(cmd)

    def close_browser(self, browser):
        script_path = os.path.join(self.hasal_dir, "lib", "sikuli")
        script_dir_path = script_path + "/closeBrowser.sikuli"
        args_list = [browser, self.set_syspath(self.hasal_dir)]
        self.run_sikulix_cmd(script_dir_path, args_list)

