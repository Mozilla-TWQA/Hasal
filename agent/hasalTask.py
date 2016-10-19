__author__ = 'shako'
import os
import sys
import json
import tarfile
import zipfile
import subprocess


class HasalTask(object):

    configurations = {}
    cmd_parameter_keys = []
    FIREFOX_BIN_LIUNX_FP = "/usr/bin/firefox"
    FIREFOX_BIN_WIN_FP   = "C:\\Program Files (x86)\\Mozilla Firefox"

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
        # Create and check backup
        backup_path = self.FIREFOX_BIN_LIUNX_FP + ".bak"
        if os.path.exists(backup_path):
            if os.path.exists(self.FIREFOX_BIN_LIUNX_FP):
                os.remove(self.FIREFOX_BIN_LIUNX_FP)
        else:
            os.rename(self.FIREFOX_BIN_LIUNX_FP, backup_path)

        if sys.platform == "linux2":
            src_link = os.path.join(os.getcwd(), "firefox", "firefox")
            os.symlink(src_link, self.FIREFOX_BIN_LIUNX_FP)
        elif sys.platform == "darwin":
            print "We are currently not support link firefox package on MAC OS!"
        else:
            src_path = os.path.join(os.getcwd(), "firefox")
            os.rename(src_path, self.FIREFOX_BIN_WIN_FP)

    def extract_fx_pkg(self, input_fx_pkg_fp):
        if input_fx_pkg_fp.endswith(".tar.bz2"):
            target_file = tarfile.open(input_fx_pkg_fp, "r:bz2")
            target_file.extractall()
            target_file.close()
        elif input_fx_pkg_fp.endswith(".zip"):
            target_file = zipfile.ZipFile(input_fx_pkg_fp, "r")
            target_file.extractall()
            target_file.close()
        else:
            print "WARNING!! We are not support extract dmg file right now!"
            return False
        return True

    def run(self):
        print "deploy fx pkg"
        self.deploy_fx_pkg()
        print "run"
        cmd_list = self.generate_command_list()
        print " ".join(cmd_list)
        self.update_svr_config()
        with open("job.log", "w") as log_fh:
            p = subprocess.Popen(cmd_list, stdout=log_fh, stderr=log_fh, env=os.environ.copy())
            p.wait()
            log_fh.flush()
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
