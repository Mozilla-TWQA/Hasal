import os
import sys

class Sikuli():
    # hasal_dir:  DEFAULT_HASAL_DIR in environment.py
    def set_syspath(self, hasal_dir):
        library_path = os.path.join(hasal_dir, "lib", "sikuli")
        sys.path.append(library_path)

    # sikuli_dir: you must specify where runsikulix or runsikulix.exe is
    # hasal_dir:  DEFAULT_HASAL_DIR in environment.py
    # test_name:  test_(browser)_(test_name)
    # timestamp:  please pass in the integer generated from main python for folder record
    def run(self, sikuli_dir, hasal_dir, test_name, timestamp):
        script_path = os.path.join(hasal_dir, "tests")
        cmd = sikuli_dir + "runsikulix -r " + script_path + test_name + ".sikuli --args " + str(timestamp)
        os.execute()

