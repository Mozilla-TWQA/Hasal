__author__ = 'shako'
import os
import sys
import json
import tarfile
import zipfile
import shutil
from lib.thirdparty.tee import system2


class HasalTask(object):

    configurations = {}
    cmd_parameter_keys = []
    FIREFOX_BIN_LINUX_FP = "/usr/bin/firefox"
    FIREFOX_BIN_WIN_FP = "C:\\Program Files (x86)\\Mozilla Firefox"
    FIREFOX_BIN_MAC_FP = "/Applications/Firefox.app"
    DEFAULT_FX_EXTRACT_DIR = "firefox"
    DEFAULT_AGENT_STATUS_DIR = os.path.join(os.getcwd(), "agent_status")
    DEFAULT_AGENT_JOB_STATUS = {'BEGIN': 'begin', 'FINISH': 'finish', 'EXCEPTION': 'exception'}
    DEFAULT_DATA_EXPIRE_DAY = 7
    DEFAULT_CONFIG_DN = "configs"
    DEFAULT_CONFIG_NAME = "default.json"
    JENKINS_CONFIG_NAME = "jenkins.json"
    DEFAULT_SUITE_NAME = "suite.txt"
    JENKINS_SUITE_NAME = "jenkins_suite.txt"
    DEFAULT_INDEX_CONFIG_NAME = "inputLatencyAnimationDctGenerator.json"

    def __init__(self, name, **kwargs):
        self.name = name
        if "path" in kwargs:
            self.src_conf_path = kwargs['path']
        self.read_configuration(**kwargs)

        # init variables
        self.DEFAULT_JOB_LOG_FN = self.configurations.get('BUILD_TAG', "jenkins-unknown-0") + ".log"
        self.BUILD_TAG = self.configurations.get('BUILD_TAG', 'jenkins-unknown-0')
        self.CURRENT_WORKING_DIR = os.path.abspath(self.configurations.get('HASAL_WORKSPACE', os.getcwd()))
        self.DEFAULT_CONFIG_DP = os.path.join(self.CURRENT_WORKING_DIR, self.DEFAULT_CONFIG_DN)

        # lambda function
        self.str2bool = lambda x: x.lower() in ['true', 'yes', 'y', '1', 'ok']

    def update(self, **kwargs):
        if 'name' in kwargs:
            self.name = kwargs['name']
        self.read_configuration(**kwargs)

    def read_configuration(self, **kwargs):
        self.configurations = kwargs
        print self.configurations

    def create_suite_file(self):
        default_suite_fp = os.path.join(self.CURRENT_WORKING_DIR, self.DEFAULT_SUITE_NAME)
        jenkins_suite_fp = os.path.join(self.CURRENT_WORKING_DIR, self.JENKINS_SUITE_NAME)
        case_list_str = self.configurations.get('CASE_LIST', None)
        if case_list_str:
            case_list = case_list_str.split(",")
        else:
            with open(default_suite_fp) as fh:
                case_list = fh.readlines()
        with open(jenkins_suite_fp, 'w') as write_fh:
            for case_path in case_list:
                write_fh.write(case_path.strip() + '\n')
        return jenkins_suite_fp

    def create_online_config(self):
        config_dn = "online"
        default_config_fp = os.path.join(self.DEFAULT_CONFIG_DP, config_dn, self.DEFAULT_CONFIG_NAME)
        output_config_fp = os.path.join(self.DEFAULT_CONFIG_DP, config_dn, self.JENKINS_CONFIG_NAME)
        with open(default_config_fp) as fh:
            config_data = json.load(fh)
        config_data['enable'] = self.str2bool(self.configurations.get('ENABLE_ONLINE', "false"))
        config_data['perfherder-revision'] = self.configurations.get('PERFHERDER_REVISION', "")
        config_data['perfherder-pkg-platform'] = self.configurations.get('PERFHERDER_PKG_PLATFORM', "")
        config_data['perfherder-suitename'] = self.configurations.get('PERFHERDER_SUITE_NAME', "")
        config_data['svr-config']['svr_addr'] = self.configurations.get('SVR_ADDR', "127.0.0.1")
        config_data['svr-config']['svr_port'] = self.configurations.get('SVR_PORT', "1234")
        config_data['svr-config']['project_name'] = self.configurations.get('PROJECT_NAME', "hasal")
        with open(output_config_fp, 'w') as write_fh:
            json.dump(config_data, write_fh)
        return output_config_fp

    def create_exec_config(self):
        config_dn = "exec"
        default_config_fp = os.path.join(self.DEFAULT_CONFIG_DP, config_dn, self.DEFAULT_CONFIG_NAME)
        output_config_fp = os.path.join(self.DEFAULT_CONFIG_DP, config_dn, self.JENKINS_CONFIG_NAME)
        with open(default_config_fp) as fh:
            config_data = json.load(fh)
        config_data['max-run'] = int(self.configurations.get('MAX_RUN', 30))
        config_data['max-retry'] = int(self.configurations.get('MAX_RETRY', 15))
        config_data['advance'] = self.str2bool(self.configurations.get('ENABLE_ADVANCE', "false"))
        config_data['comment'] = self.configurations.get('EXEC_COMMENT', "<today>")
        config_data['exec-suite-fp'] = self.create_suite_file()
        config_data['output-result-ipynb-file'] = self.str2bool(self.configurations.get('OUTPUT_RESULT_IPYNB_FILE', "false"))
        config_data['output-result-video-file'] = self.str2bool(self.configurations.get('OUTPUT_RESULT_VIDEO_FILE', "true"))
        with open(output_config_fp, 'w') as write_fh:
            json.dump(config_data, write_fh)
        return output_config_fp

    def create_firefox_config(self):
        config_dn = "firefox"
        default_config_fp = os.path.join(self.DEFAULT_CONFIG_DP, config_dn, self.configurations.get('FIREFOX_CONFIG_NAME', self.DEFAULT_CONFIG_NAME))
        output_config_fp = os.path.join(self.DEFAULT_CONFIG_DP, config_dn, self.JENKINS_CONFIG_NAME)
        with open(default_config_fp) as fh:
            config_data = json.load(fh)

        # you can add the config modification here to reflect Jenkins's setting

        with open(output_config_fp, 'w') as write_fh:
            json.dump(config_data, write_fh)
        return output_config_fp

    def create_index_config(self):
        config_dn = "index"
        default_config_fp = os.path.join(self.DEFAULT_CONFIG_DP, config_dn, self.configurations.get('INDEX_CONFIG_NAME', self.DEFAULT_INDEX_CONFIG_NAME))
        output_config_fp = os.path.join(self.DEFAULT_CONFIG_DP, config_dn, self.JENKINS_CONFIG_NAME)
        with open(default_config_fp) as fh:
            config_data = json.load(fh)

        # you can add the config modification here to reflect Jenkins's setting

        with open(output_config_fp, 'w') as write_fh:
            json.dump(config_data, write_fh)
        return output_config_fp

    def generate_command_list(self):
        result_list = ['python', 'runtest.py', '--firefox-config', self.create_firefox_config(), '--index-config',
                       self.create_index_config(), '--exec-config', self.create_exec_config(), '--online-config',
                       self.create_online_config()]
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
        # Move default firefox to backup folder, and we want to always keep one copy of default firefox package,
        # so we won't always replace the backup one.
        backup_path = firefox_fp + ".bak"
        if os.path.exists(backup_path):
            if os.path.exists(firefox_fp):
                if sys.platform == "linux2":
                    os.remove(firefox_fp)
                else:
                    shutil.rmtree(firefox_fp)
        else:
            if os.path.exists(firefox_fp):
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
            if os.path.exists(self.DEFAULT_FX_EXTRACT_DIR):
                shutil.rmtree(self.DEFAULT_FX_EXTRACT_DIR)
            target_file = tarfile.open(input_fx_pkg_fp, "r:bz2")
            target_file.extractall()
            target_file.close()
        elif input_fx_pkg_fp.endswith(".zip"):
            if os.path.exists(self.DEFAULT_FX_EXTRACT_DIR):
                shutil.rmtree(self.DEFAULT_FX_EXTRACT_DIR)
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
        # remove created log
        if os.path.exists(self.DEFAULT_JOB_LOG_FN):
            os.remove(self.DEFAULT_JOB_LOG_FN)
            print "WARNING: job.log [%s] exist, removed right now!" % self.DEFAULT_JOB_LOG_FN

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

        # create agent status dir if not exist
        if os.path.exists(self.DEFAULT_AGENT_STATUS_DIR) is False:
            os.mkdir(self.DEFAULT_AGENT_STATUS_DIR)

    def touch_status_file(self, status):
        current_status_fp = os.path.join(self.DEFAULT_AGENT_STATUS_DIR, self.BUILD_TAG + "." + status)
        with open(current_status_fp, 'w') as write_fh:
            write_fh.write(" ")

    def teardown_job(self):
        # touch finish status
        self.touch_status_file(self.DEFAULT_AGENT_JOB_STATUS['FINISH'])

    def run(self):
        # clean up the environment
        self.init_environment()

        # job start running log
        print "INFO: Job [%s] start running" % self.src_conf_path

        # touch begin status
        self.touch_status_file(self.DEFAULT_AGENT_JOB_STATUS['BEGIN'])

        # start running
        print "INFO: start to deploy Firefox package"
        self.deploy_fx_pkg()
        print "INFO: generate new config for Jenkins running Hasal"
        cmd_list = self.generate_command_list()
        print "INFO: start to trigger runtest.py"
        str_exec_cmd = " ".join(cmd_list)
        print str_exec_cmd
        try:
            system2(str_exec_cmd, logger=self.DEFAULT_JOB_LOG_FN, stdout=True, exec_env=os.environ.copy())
        except Exception as e:
            print e.message

        # remove json file
        if os.path.exists(self.src_conf_path):
            os.remove(self.src_conf_path)
            print "INFO: running test finished! Json configuration file [%s] removed!" % self.src_conf_path

        # teardown of this task
        self.teardown_job()

    def onstop(self):
        print "===== onstop ====="
        print self.src_conf_path
        if os.path.exists(self.src_conf_path):
            os.remove(self.src_conf_path)
            print "INFO: onstop event, json configuration file [%s] removed!" % self.src_conf_path
        # teardown of this task
        self.teardown_job()

    def teardown(self):
        print "===== teardown ====="
        print self.src_conf_path
        if os.path.exists(self.src_conf_path):
            os.remove(self.src_conf_path)
            print "INFO: tear down event, json configuration file [%s] removed!" % self.src_conf_path
        # teardown of this task
        self.teardown_job()
