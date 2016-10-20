"""

Usage:
  generate_suite_file.py [-s=<str>]
  generate_suite_file.py (-h | --help)

Options:
  -h --help                 Show this screen.
  -s=<str>                  The path of suite folder located [default: .].
"""
import os
from docopt import docopt


class GenerateSuiteFile(object):
    TEST_TYPE_PT = 'pilot'
    TEST_TYPE_RE = 'regression'
    FOLDER_CHECK_LIST = [TEST_TYPE_PT, TEST_TYPE_RE]

    def scan(self, input_path):
        if input_path.endswith(os.sep):
            input_path = input_path[:-1]
        scan_path = input_path.split(os.sep)[-1]
        suite_path = os.path.join(os.getcwd(), input_path)
        scan_file_list = [scan_name for scan_name in os.listdir(suite_path) if scan_name in self.FOLDER_CHECK_LIST]
        if len(scan_file_list) == len(self.FOLDER_CHECK_LIST):
            for test_type in scan_file_list:
                self.generate_suite_file(test_type, scan_path, suite_path)
        else:
            print "ERROR: the path you specify didn't contain the required folder list [%s]" % self.FOLDER_CHECK_LIST

    def generate_suite_file(self, type, scan_path, suite_path):
        testtype_dp = os.path.join(suite_path, type)
        webapp_list = [wname for wname in os.listdir(testtype_dp) if
                       wname.endswith(".py") is False and wname.startswith(".") is False and wname.endswith(
                           ".suite") is False and wname.endswith(".pyc") is False]
        for webapp in webapp_list:
            output_fn = os.path.join(testtype_dp, webapp + ".suite")
            with open(output_fn, 'w') as write_fh:
                webapp_dp = os.path.join(testtype_dp, webapp)
                for f_name in os.listdir(webapp_dp):
                    if type == self.TEST_TYPE_PT:
                        if f_name.endswith(".sikuli"):
                            case_name = os.sep.join([scan_path, type, webapp, f_name])
                            write_fh.write(case_name + os.linesep)
                    elif type == self.TEST_TYPE_RE:
                        if f_name.endswith(".py") and f_name != "__init__.py":
                            case_name = ".".join(
                                [scan_path, type, webapp, f_name.split(".")[0]])
                            write_fh.write(case_name + os.linesep)
                    else:
                        print "ERROR: unknown test type [%s]" % type


def main():
    arguments = docopt(__doc__)
    gen_suite_obj = GenerateSuiteFile()
    gen_suite_obj.scan(arguments['-s'])

if __name__ == '__main__':
    main()
