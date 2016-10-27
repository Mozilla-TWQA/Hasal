__author__ = 'shako'
import os
import sys
import json
import time
import tarfile
import zipfile
import shutil
import subprocess


class HasalTask(object):

    configurations = {}
    cmd_parameter_keys = []
    FIREFOX_BIN_LINUX_FP = "/usr/bin/firefox"
    FIREFOX_BIN_WIN_FP = "C:\\Program Files (x86)\\Mozilla Firefox"
    FIREFOX_BIN_MAC_FP = "/Applications/Firefox.app"
    DEFAULT_JOB_LOG_FN = "job.log"
    DEFAULT_DATA_EXPIRE_DAY = 14

    def __init__(self, name, **kwargs):
        self.name = name
        if "path" in kwargs:
            self.src_conf_path = kwargs['path']
        self.read_configuration(**kwargs)

    def update(self, **kwargs):
        if 'name' in kwargs:
            self.name = kwargs['name']
        self.read_configuration(**kwargs)

    def read_configuration(self, **kwargs):
        self.configurations = kwargs
        print self.configurations

    def update_svr_config(self):
        updated_key = ['svr_addr', 'svr_port', 'project_name']
        config_dict = {}
        for key in self.configurations:
            if key.lower() in updated_key:
                config_dict[key.lower()] = self.configurations[key]
        with open('svrConfig.json', 'w') as svrconfig_fh:
            json.dump(config_dict, svrconfig_fh)

    def generate_command_list(self):
        result_list = ['python', 'runtest.py', self.configurations['TYPE']]
        suite_fn = ".".join(['suite', self.configurations['TYPE'], self.configurations['SUITE']])
        if self.configurations['SUITE'] == "others":
            # Generate others suite file for this job
            with open(suite_fn, "w") as suite_fh:
                case_name_list = self.configurations['OTHERS'].split(",")
                for case_name in case_name_list:
                    if self.configurations['TYPE'] == 're':
                        case_full_name = ".".join(
                            ['tests', 'regression', case_name.split("_")[2], case_name])
                    else:
                        case_full_name = os.sep.join(['tests', 'pilot', case_name.split("_")[2], case_name])
                    suite_fh.write(case_full_name + os.linesep)
        else:
            # Generate suite file for selected web application
            if self.configurations['TYPE'] == 're':
                case_dir = os.path.join(os.getcwd(), 'tests', 'regression', self.configurations['SUITE'])
                with open(suite_fn, 'w') as suite_fh:
                    for f_name in os.listdir(case_dir):
                        if f_name.endswith(".py") and f_name != "__init__.py":
                            case_name = ".".join(['tests', 'regression', self.configurations['SUITE'], f_name.split(".")[0]])
                            suite_fh.write(case_name + os.linesep)
            else:
                case_dir = os.path.join(os.getcwd(), 'tests', 'pilot', self.configurations['SUITE'])
                with open(suite_fn, 'w') as suite_fh:
                    for f_name in os.listdir(case_dir):
                        if f_name.endswith(".sikuli"):
                            case_name = os.sep.join(['tests', 'pilot', self.configurations['SUITE'], f_name])
                            suite_fh.write(case_name + os.linesep)
        result_list.append(suite_fn)

        # Combine the parameter with cmd list
        for key in self.configurations:
            if key.startswith("--"):
                if self.configurations[key] == 'true':
                    result_list.append(key.lower())
                elif self.configurations[key] != 'false':
                    result_list.append(key.lower() + "=" + self.configurations[key])
        return result_list

    def deploy_fx_pkg(self):
        if "FX-DL-PACKAGE-PATH" in self.configurations:
            if self.extract_fx_pkg(self.configurations['FX-DL-PACKAGE-PATH']):
                self.link_fx_pkg()
        else:
            print "Use current firefox browser instead of deploying a new firefox package"

    def link_fx_pkg(self):
        if sys.platform == "linux2":
            firefox_fp = self.FIREFOX_BIN_LINUX_FP
        elif sys.platform == "win32":
            firefox_fp = self.FIREFOX_BIN_WIN_FP
        else:
            firefox_fp = self.FIREFOX_BIN_MAC_FP
        # Create and check backup
        backup_path = firefox_fp + ".bak"
        if os.path.exists(backup_path):
            if os.path.exists(firefox_fp):
                if sys.platform == "linux2":
                    os.remove(firefox_fp)
                else:
                    shutil.rmtree(firefox_fp)
        else:
            os.rename(firefox_fp, backup_path)

        if sys.platform == "linux2":
            src_link = os.path.join(os.getcwd(), "firefox", "firefox")
            os.symlink(src_link, self.FIREFOX_BIN_LINUX_FP)
        elif sys.platform == "darwin":
            DEFAULT_NIGHLTY_ATTACTED_PATH = "/Volumes/Nightly"
            if os.path.exists(DEFAULT_NIGHLTY_ATTACTED_PATH):
                shutil.copytree(os.path.join(DEFAULT_NIGHLTY_ATTACTED_PATH, "FirefoxNightly.app"), self.FIREFOX_BIN_MAC_FP)
                detach_cmd_format = "hdiutil detach %s"
                detach_cmd_str = detach_cmd_format % DEFAULT_NIGHLTY_ATTACTED_PATH
                if os.system(detach_cmd_str) != 0:
                    print "ERROR: detach dmg file[%s] failed! cmd string: [%s]" % (DEFAULT_NIGHLTY_ATTACTED_PATH, detach_cmd_str)
            else:
                print "ERROR: can't find the nightly attached path [%s]" % DEFAULT_NIGHLTY_ATTACTED_PATH
        else:
            src_path = os.path.join(os.getcwd(), "firefox")
            os.rename(src_path, self.FIREFOX_BIN_WIN_FP)

    def extract_fx_pkg(self, input_fx_pkg_fp):
        if input_fx_pkg_fp.endswith(".tar.bz2"):
            shutil.rmtree("firefox")
            target_file = tarfile.open(input_fx_pkg_fp, "r:bz2")
            target_file.extractall()
            target_file.close()
        elif input_fx_pkg_fp.endswith(".zip"):
            shutil.rmtree("firefox")
            target_file = zipfile.ZipFile(input_fx_pkg_fp, "r")
            target_file.extractall()
            target_file.close()
        else:
            attach_cmd_format = "hdiutil attach -noautoopen -quiet %s"
            attach_cmd_str = attach_cmd_format % input_fx_pkg_fp
            if os.system(attach_cmd_str) != 0:
                print "ERROR: attach dmg file[%s] failed! cmd string: [%s]" % (input_fx_pkg_fp, attach_cmd_str)
                return False
            else:
                print "INFO: attach dmg file[%s] sucessfully!" % input_fx_pkg_fp
        return True

    def init_environment(self):
        # kill legacy process
        if sys.platform == "linux2":
            DEFAULT_TASK_KILL_LIST = ["avconv", "firefox", "chrome"]
            DEFAULT_TASK_KILL_CMD = "pkill "
        elif sys.platform == "win32":
            DEFAULT_TASK_KILL_CMD = "taskkill /f /t /im "
            DEFAULT_TASK_KILL_LIST = ["ffmpeg", "firefox.exe", "chrome.exe"]
        else:
            DEFAULT_TASK_KILL_LIST = ["ffmpeg", "firefox", "chrome"]
            DEFAULT_TASK_KILL_CMD = "pkill "
        for process_name in DEFAULT_TASK_KILL_LIST:
            cmd_str = DEFAULT_TASK_KILL_CMD + process_name
            os.system(cmd_str)

        # remove created log
        if os.path.exists(self.DEFAULT_JOB_LOG_FN):
            os.remove(self.DEFAULT_JOB_LOG_FN)

        # clean output folder
        output_dir_list = []
        output_dir = os.path.join(os.getcwd(), 'output')
        output_dir_list.append(os.path.join(output_dir, 'images', 'output'))
        output_dir_list.append(os.path.join(output_dir, 'images', 'sample'))
        output_dir_list.append(os.path.join(output_dir, 'profiles'))
        output_dir_list.append(os.path.join(output_dir, 'videos'))
        for output_dir in output_dir_list:
            for target_name in os.listdir(output_dir):
                check_target = os.path.join(output_dir, target_name)
                if (time.time() - os.path.getmtime(check_target)) > (60 * 60 * 24 * self.DEFAULT_DATA_EXPIRE_DAY):
                    print "INFO: housekeeping the exisitng output dir/file [%s]" % check_target
                    if os.path.isdir(check_target):
                        shutil.rmtree(check_target)
                    else:
                        os.remove(check_target)

    def run(self):
        # clean up the environment
        self.init_environment()

        # start running
        with open(self.DEFAULT_JOB_LOG_FN, "w+") as log_fh:
            sys.stdout = log_fh
            sys.stderr = log_fh
            print "deploy fx pkg"
            self.deploy_fx_pkg()
            print "run"
            cmd_list = self.generate_command_list()
            print " ".join(cmd_list)
            self.update_svr_config()
            subprocess.call(cmd_list, stdout=log_fh, stderr=log_fh, env=os.environ.copy())

        # remove json file
        os.remove(self.src_conf_path)

    def onstop(self):
        print "===== onstop ====="
        print self.src_conf_path
        if os.path.exists(self.src_conf_path):
            os.remove(self.src_conf_path)

    def teardown(self):
        print "===== teardown ====="
        print self.src_conf_path
        if os.path.exists(self.src_conf_path):
            os.remove(self.src_conf_path)
