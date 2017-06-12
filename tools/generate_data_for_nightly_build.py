"""

Usage:
  generate_data_for_nightly_build.py [-i=<str>]
  generate_data_for_nightly_build.py (-h | --help)

Options:
  -h --help                 Show this screen.
  -i=<str>                  Specify config json
"""
import re
import os
import sys
import shutil
import json
import tarfile
import zipfile
import urllib2
import requests
import platform
import subprocess

from docopt import docopt
from tqdm import tqdm


class GenerateData(object):
    ARCHIVE_URL = "https://archive.mozilla.org"
    NIGHTLY_URL_FOLDER = "/pub/firefox/nightly/"

    FIREFOX_BIN_LINUX_FP = "/usr/bin/firefox"
    FIREFOX_BIN_WIN_FP = "C:\\Program Files (x86)\\Mozilla Firefox"
    FIREFOX_BIN_MAC_FP = "/Applications/Firefox.app"

    PLATFORM_FN_MAPPING = {'linux32': {'key': 'linux-i686', 'ext': 'tar.bz2', 'trydl': 'linux', 'job': ['linux32']},
                           'linux64': {'key': 'linux-x86_64', 'ext': 'tar.bz2', 'trydl': 'linux64', 'job': ['linux64']},
                           'mac': {'key': 'mac', 'ext': 'dmg', 'trydl': 'macosx64', 'job': ['osx']},
                           'win32': {'key': 'win32', 'ext': 'zip', 'trydl': 'win32', 'job': ['windows', '32']},
                           'win64': {'key': 'win64', 'ext': 'zip', 'trydl': 'win64', 'job': ['windows', '64']}}

    BUILDBOT_MAPPING_PLATFORM = {"linux-i686": {"_": "linux32"},
                                 "linux-x86_64": {"_": "linux64"},
                                 "mac": {"_": "osx-10-10"},
                                 "win32": {"_": "windows7-32"},
                                 "win64": {"_": "windows8-64",
                                           "7": "windows8-64",
                                           "10": "windows10-64"}
                                 }

    DEFAULT_CONFIG_DN = "configs"
    DEFAULT_FX_EXTRACT_DIR = "firefox"
    DEFAULT_CONFIG_NAME = "default.json"
    DEFAULT_INDEX_CONFIG_NAME = "inputLatencyAnimationDctGenerator.json"
    DEFAULT_COFNIG_FN = "generatedata.json"

    CONFIG_KEY_NIGHTLY_BUILD_DATE_LIST = "nightly_build_date_list"
    CONFIG_KEY_PKG_TARGET_PLATFORM = "pkg_target_platform"
    CONFIG_KEY_TMP_OUTPUT_DP = "tmp_output_dp"
    CONFIG_KEY_PLATFORM_OPT = "platform_opt"
    CONFIG_KEY_OUTPUT_CONFIG_DP = "output_config_dp"
    CONFIG_KEY_SUITE_DICT = "suite_dict"

    def __init__(self, input_config_path):
        with open(input_config_path) as fh:
            self.configuration = json.load(fh)
        self.platform = self.configuration.get(self.CONFIG_KEY_PKG_TARGET_PLATFORM, sys.platform)
        self.output_dp = self.configuration.get(self.CONFIG_KEY_TMP_OUTPUT_DP, os.getcwd())
        self.platform_option = self.configuration.get(self.CONFIG_KEY_PLATFORM_OPT, 'opt')
        self.output_config_dp = os.path.join(os.getcwd(), self.configuration.get(self.CONFIG_KEY_OUTPUT_CONFIG_DP, 'output_config'))
        self.DEFAULT_CONFIG_DP = os.path.join(os.getcwd(), self.DEFAULT_CONFIG_DN)
        self.suite_data = self.configuration.get(self.CONFIG_KEY_SUITE_DICT, {})
        self.str2bool = lambda x: x.lower() in ['true', 'yes', 'y', '1', 'ok']

        if not os.path.exists(self.output_config_dp):
            os.mkdir(self.output_config_dp)

    def create_suite_file(self, output_config_dp, suite_name, suite_dict):
        suite_fp = os.path.join(output_config_dp, suite_name + ".suite")
        if not os.path.exists(suite_fp):
            with open(suite_fp, 'w') as write_fh:
                for case_path in suite_dict[suite_name]['case_list']:
                    write_fh.write(case_path.strip() + '\n')
        return suite_fp

    def create_online_config(self, output_config_fn, perfherder_revision, perfherder_pkg_platform, perfherder_suite_name):
        config_dn = "online"
        default_config_fp = os.path.join(self.DEFAULT_CONFIG_DP, config_dn, self.DEFAULT_CONFIG_NAME)
        output_config_dp = os.path.join(self.output_config_dp, config_dn)
        output_config_fp = os.path.join(self.output_config_dp, config_dn, output_config_fn)
        if not os.path.exists(output_config_dp):
            os.mkdir(output_config_dp)
        if not os.path.exists(output_config_fp):
            with open(default_config_fp) as fh:
                config_data = json.load(fh)
            config_data['enable'] = self.str2bool(self.configuration.get('ENABLE_ONLINE', "false"))
            config_data['perfherder-revision'] = perfherder_revision
            config_data['perfherder-pkg-platform'] = perfherder_pkg_platform
            config_data['perfherder-suitename'] = perfherder_suite_name
            config_data['svr-config']['svr_addr'] = self.configuration.get('SVR_ADDR', "127.0.0.1")
            config_data['svr-config']['svr_port'] = self.configuration.get('SVR_PORT', "1234")
            config_data['svr-config']['project_name'] = self.configuration.get('PROJECT_NAME', "hasal")
            with open(output_config_fp, 'w') as write_fh:
                json.dump(config_data, write_fh)
        return output_config_fp

    def create_exec_config(self, output_config_fn, suite_fp):
        config_dn = "exec"
        default_config_fp = os.path.join(self.DEFAULT_CONFIG_DP, config_dn, self.DEFAULT_CONFIG_NAME)
        output_config_dp = os.path.join(self.output_config_dp, config_dn)
        output_config_fp = os.path.join(self.output_config_dp, config_dn, output_config_fn)
        if not os.path.exists(output_config_dp):
            os.mkdir(output_config_dp)
        if not os.path.exists(output_config_fp):
            with open(default_config_fp) as fh:
                config_data = json.load(fh)
            config_data['max-run'] = int(self.configuration.get('MAX_RUN', 30))
            config_data['max-retry'] = int(self.configuration.get('MAX_RETRY', 15))
            config_data['advance'] = self.str2bool(self.configuration.get('ENABLE_ADVANCE', "false"))
            config_data['comment'] = self.configuration.get('EXEC_COMMENT', "<today>")
            config_data['exec-suite-fp'] = suite_fp
            with open(output_config_fp, 'w') as write_fh:
                json.dump(config_data, write_fh)
        return output_config_fp

    def create_firefox_config(self, output_config_fn):
        config_dn = "firefox"
        default_config_fp = os.path.join(self.DEFAULT_CONFIG_DP, config_dn, self.configuration.get('FIREFOX_CONFIG_NAME', self.DEFAULT_CONFIG_NAME))
        output_config_dp = os.path.join(self.output_config_dp, config_dn)
        output_config_fp = os.path.join(self.output_config_dp, config_dn, output_config_fn)
        if not os.path.exists(output_config_dp):
            os.mkdir(output_config_dp)
        if not os.path.exists(output_config_fp):
            with open(default_config_fp) as fh:
                config_data = json.load(fh)

            # you can add the config modification here to reflect Jenkins's setting

            with open(output_config_fp, 'w') as write_fh:
                json.dump(config_data, write_fh)
        return output_config_fp

    def create_index_config(self, output_config_fn):
        config_dn = "index"
        default_config_fp = os.path.join(self.DEFAULT_CONFIG_DP, config_dn, self.configuration.get('INDEX_CONFIG_NAME', self.DEFAULT_INDEX_CONFIG_NAME))
        output_config_dp = os.path.join(self.output_config_dp, config_dn)
        output_config_fp = os.path.join(self.output_config_dp, config_dn, output_config_fn)
        if not os.path.exists(output_config_dp):
            os.mkdir(output_config_dp)
        if not os.path.exists(output_config_fp):
            with open(default_config_fp) as fh:
                config_data = json.load(fh)

            # you can add the config modification here to reflect Jenkins's setting

            with open(output_config_fp, 'w') as write_fh:
                json.dump(config_data, write_fh)
        return output_config_fp

    def generate_command_list(self, nightly_build_date_id, suite_name, suite_fp, perfherder_revision, perfherder_pkg_platform, perfherder_suite_name):
        exec_output_config_fn = suite_name + ".json"
        online_output_config_fn = nightly_build_date_id + "-" + suite_name + ".json"
        result_list = ['python', 'runtest.py', '--firefox-config', self.create_firefox_config(self.DEFAULT_COFNIG_FN), '--index-config',
                       self.create_index_config(self.DEFAULT_COFNIG_FN), '--exec-config', self.create_exec_config(exec_output_config_fn, suite_fp), '--online-config',
                       self.create_online_config(online_output_config_fn, perfherder_revision, perfherder_pkg_platform, perfherder_suite_name)]
        return result_list

    def trigger(self):

        nightly_build_list = self.configuration.get(self.CONFIG_KEY_NIGHTLY_BUILD_DATE_LIST, [])

        for nightly_build_date_dn in nightly_build_list:

            nightly_build_date_id = nightly_build_date_dn.split("/")[-2]

            # download nightly build
            download_fx_fp, download_json_fp = self.get_nightly_build(nightly_build_date_dn, self.output_dp)

            # check download result
            if download_fx_fp is None or download_json_fp is None:
                print "ERROR: something wrong with your build download process, please check the setting and job status."
                sys.exit(1)
            else:
                # link firefox package to correct path
                if self.extract_fx_pkg(download_fx_fp):
                    self.link_fx_pkg()

                # get config value from nightly json file
                with open(download_json_fp) as dl_json_fh:
                    dl_json_data = json.load(dl_json_fh)
                current_platform_release = platform.release().strip()
                perfherder_revision = dl_json_data['moz_source_stamp']
                build_pkg_platform = dl_json_data['moz_pkg_platform']

                # mapping the perfherder pkg platform to nomenclature of builddot
                if current_platform_release in self.BUILDBOT_MAPPING_PLATFORM[build_pkg_platform].keys():
                    perfherder_pkg_platform = self.BUILDBOT_MAPPING_PLATFORM[build_pkg_platform][
                        current_platform_release]
                else:
                    perfherder_pkg_platform = self.BUILDBOT_MAPPING_PLATFORM[build_pkg_platform]["_"]

                # loop suite file
                for suite_name in self.suite_data:

                    # create suite file
                    print "working on suite fp [%s]" % suite_name
                    suite_fp = self.create_suite_file(self.output_config_dp, suite_name, self.suite_data)

                    # generate command list
                    cmd_list = self.generate_command_list(nightly_build_date_id, suite_name, suite_fp, perfherder_revision,
                                                          perfherder_pkg_platform,
                                                          self.suite_data[suite_name]['perfherder_suite_name'])
                    print " ".join(cmd_list)
                    subprocess.call(cmd_list, env=os.environ.copy())

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

    def get_files_from_remote_url_folder(self, remote_url_str):
        return_dict = {}
        try:
            response_obj = urllib2.urlopen(remote_url_str)
            if response_obj.getcode() == 200:
                for line in response_obj.readlines():
                    match = re.search(r'(?<=href=").*?(?=")', line)
                    if match:
                        href_link = match.group(0)
                        f_name = href_link.split("/")[-1]
                        return_dict[f_name] = href_link
            else:
                print "ERROR: fetch remote file list error with code [%s]" % str(response_obj.getcode())
        except Exception as e:
            print "ERROR: [%s]" % e.message
        return return_dict

    def download_file(self, output_dp, download_link):
        print "Prepare to download the build from link [%s]" % download_link
        response = requests.get(download_link, verify=False, stream=True)
        download_fn = download_link.split("/")[-1]
        if os.path.exists(output_dp) is False:
            os.makedirs(output_dp)
        download_fp = os.path.join(output_dp, download_fn)
        try:
            try:
                total_len = int(response.headers['content-length'])
            except:
                total_len = None
            with open(download_fp, 'wb') as fh:
                for data in tqdm(response.iter_content(chunk_size=512 * 1024), total=total_len / (512 * 1024)):
                    fh.write(data)
            return download_fp
        except Exception as e:
            print "ERROR: [%s]" % e.message
            return None

    def download_from_remote_url_folder(self, remote_url_str, output_dp):
        # get latest nightly build list from remote url folder
        remote_file_dict = self.get_files_from_remote_url_folder(remote_url_str)

        # filter with platform, and return file name with extension
        if len(remote_file_dict.keys()) == 0:
            print "ERROR: can't get remote file list, could be the network error, or url path[%s] wrong!!" % remote_url_str
            return False
        else:
            if self.platform not in self.PLATFORM_FN_MAPPING:
                print "ERROR: we are currently not support the platform[%s] you specified!" % self.platform
                print "We are currently support the platform tag: [%s]" % self.PLATFORM_FN_MAPPING.keys()
                return False
            else:
                matched_keyword = self.PLATFORM_FN_MAPPING[self.platform]['key'] + "." + self.PLATFORM_FN_MAPPING[self.platform]['ext']
                matched_file_list = [fn for fn in remote_file_dict.keys()
                                     if ((matched_keyword in fn) and ('firefox' in fn) and (not fn.endswith('.asc')))]
                if len(matched_file_list) != 1:
                    print "WARN: the possible match file list is not equal 1, list as below: [%s]" % matched_file_list
                    if len(matched_file_list) < 1:
                        return False
                    matched_file_list = sorted(matched_file_list)[-1:]
                    print "WARN: select following file [%s]" % matched_file_list

        # combine file name with json
        matched_file_name = matched_file_list[0]
        json_file_name = matched_file_name.replace(
            self.PLATFORM_FN_MAPPING[self.platform]['key'] + "." + self.PLATFORM_FN_MAPPING[self.platform]['ext'],
            self.PLATFORM_FN_MAPPING[self.platform]['key'] + ".json")
        if json_file_name not in remote_file_dict:
            print "ERROR: can't find the json file[%s] in remote file list[%s]!" % (json_file_name, remote_file_dict)
            return False
        else:
            print "DEBUG: matched file name: [%s], json_file_name: [%s]" % (matched_file_name, json_file_name)

        # download files
        download_fx_url = self.ARCHIVE_URL + remote_file_dict[matched_file_name]
        download_fx_fp = self.download_file(output_dp, download_fx_url)
        download_json_url = self.ARCHIVE_URL + remote_file_dict[json_file_name]
        download_json_fp = self.download_file(output_dp, download_json_url)

        # check download status
        if download_fx_fp and download_json_fp:
            print "SUCCESS: build files download in [%s], [%s] " % (download_fx_fp, download_json_fp)
            return (download_fx_fp, download_json_fp)
        else:
            print "ERROR: build files download in [%s,%s] " % (download_fx_fp, download_json_fp)
            return None

    def get_nightly_build(self, build_dir_name, output_dp):
        remote_url_str = self.ARCHIVE_URL + self.NIGHTLY_URL_FOLDER + build_dir_name
        return self.download_from_remote_url_folder(remote_url_str, output_dp)


def main():
    arguments = docopt(__doc__)
    if arguments['-i']:
        if not os.path.exists(arguments['-i']):
            print "ERROR: Cannot find the specify config path"
            sys.exit(1)
    else:
        print "ERROR: Please specify the json config"
        sys.exit(1)

    generate_data_obj = GenerateData(arguments['-i'])
    generate_data_obj.trigger()

if __name__ == '__main__':
    main()
