import os
import sys
import json
import shutil
import platform
import logging
import tarfile
import zipfile
from baseTasks import init_task
from baseTasks import parse_cmd_parameters
from lib.common.commonUtil import NetworkUtil
from lib.helper.archiveMozillaHelper import ArchiveMozillaHelper


FIREFOX_BIN_LINUX_FP = "/usr/bin/firefox"
FIREFOX_BIN_WIN_FP = "C:\\Program Files (x86)\\Mozilla Firefox"
FIREFOX_BIN_MAC_FP = "/Applications/Firefox.app"


def download_from_remote_url_folder(dl_pkg_platform, remote_url_str, output_dp):
    """
    get latest nightly build list from remote url folder
    @param dl_pkg_platform: linux64/mac/win64
    @param remote_url_str: https://archive...etc.
    @param output_dp: output directory path
    @return: True: success, False exception happened
    """
    fx_pkg_name_url_path, fx_pkg_json_url_path = ArchiveMozillaHelper.get_fx_pkg_name(dl_pkg_platform, remote_url_str)

    # download files
    if fx_pkg_json_url_path and fx_pkg_json_url_path:
        download_fx_url = ArchiveMozillaHelper.DEFAULT_ARCHIVE_URL + fx_pkg_name_url_path
        download_fx_fp = NetworkUtil.download_file(output_dp, download_fx_url)
        download_json_url = ArchiveMozillaHelper.DEFAULT_ARCHIVE_URL + fx_pkg_json_url_path
        download_json_fp = NetworkUtil.download_file(output_dp, download_json_url)
    else:
        logging.error("Failed to get the reference fx pkg json and fn path")
        return None, None

    # check download status
    if download_fx_fp and download_json_fp:
        logging.info("SUCCESS: build files download in [%s], [%s] " % (download_fx_fp, download_json_fp))
        return (download_fx_fp, download_json_fp)
    else:
        logging.error("build files download in [%s,%s] " % (download_fx_fp, download_json_fp))
        return None, None


def download_nightly_build(output_dp, remote_url_str):
    """
    download nightly build based the url folder name your provided
    @param
     ouput_dp: the path where your downloaded firefox package want to store, default: current dir
     remote_url_str: archive url

    @return:
    """

    # init return result
    return_result = {}

    # init platform value
    if sys.platform == "linux2":
        dl_pkg_platform = "linux64"
    elif sys.platform == "darwin":
        dl_pkg_platform = "mac"
    else:
        dl_pkg_platform = "win64"

    return_result['output_dp'] = output_dp

    # get download fx package local path and json path
    download_fx_fp, download_json_fp = download_from_remote_url_folder(dl_pkg_platform, remote_url_str, output_dp)
    return_result['FX-DL-PACKAGE-PATH'] = download_fx_fp
    return_result['FX-DL-JSON-PATH'] = download_json_fp

    if download_fx_fp is None or download_json_fp is None:
        logging.error("something wrong with your build download process, please check the setting and job status.")
        return return_result
    else:
        current_platform_release = platform.release().strip()

        # parse downloaded fx pkg json file
        with open(download_json_fp) as dl_json_fh:
            dl_json_data = json.load(dl_json_fh)
            perfherder_revision = dl_json_data['moz_source_stamp']
            build_pkg_platform = dl_json_data['moz_pkg_platform']
            # mapping the perfherder pkg platform to nomenclature of builddot
            builddot_mapping_platform = {"linux-i686": {"_": "linux32"},
                                         "linux-x86_64": {"_": "linux64"},
                                         "mac": {"_": "osx-10-10"},
                                         "win32": {"_": "windows7-32"},
                                         "win64": {"_": "windows8-64",
                                                   "7": "windows8-64",
                                                   "10": "windows10-64"}
                                         }

            return_result['PERFHERDER-REVISION'] = perfherder_revision
            if current_platform_release in builddot_mapping_platform[build_pkg_platform].keys():
                return_result['PERFHERDER-PKG-PLATFORM'] = builddot_mapping_platform[build_pkg_platform][
                    current_platform_release]
            else:
                return_result['PERFHERDER-PKG-PLATFORM'] = builddot_mapping_platform[build_pkg_platform]["_"]

        return return_result


def download_specify_url_nightly_build(**kwargs):
    """
    Download speicfy date url nightly build, the url means the full path after https://archive.mozilla.org/pub/firefox/nightly
    @param kwargs:

        kwargs['cmd_obj']['configs']['DOWNLOAD_PKG_OUTPUT_DP'] :: the path where your downloaded firefox package want to store, default: current dir
        kwargs['cmd_obj']['configs']['DOWNLOAD_PKG_DIR_URL'] :: the full path after https://archive.mozilla.org/pub/firefox/nightly

    @return: json obj
    {
        "output_dp":
        "FX-DL-PACKAGE-PATH":
        "FX-DL-JSON-PATH":
        "PERFHERDER-REVISION":
        "PERFHERDER-PKG-PLATFORM":
    }

    """

    # get queue msg, consumer config from kwargs
    queue_msg, consumer_config, task_config = init_task(kwargs)

    # get output dir path from kwargs
    cmd_parameter_list = parse_cmd_parameters(queue_msg)
    if len(cmd_parameter_list) == 3:
        output_dp = cmd_parameter_list[1]
        download_dir_url_path = cmd_parameter_list[2]
    else:
        output_dp = task_config.get("DOWNLOAD_PKG_OUTPUT_DP", os.getcwd())
        download_dir_url_path = task_config.get("DOWNLOAD_PKG_DIR_URL", "")

    # init download url
    remote_url_str = ArchiveMozillaHelper.DEFAULT_ARCHIVE_URL + ArchiveMozillaHelper.DEFAULT_NIGHTLY_ARCHIVE_URL_DIR + download_dir_url_path

    return download_nightly_build(output_dp, remote_url_str)


def download_latest_nightly_build(**kwargs):
    """
    you can specify output_dp in task configs or after the cmd
    @param kwargs:

        kwargs['cmd_obj']['configs']['DOWNLOAD_PKG_OUTPUT_DP'] :: the path where your downloaded firefox package want to store, default: current dir

    @return: json obj
    {
        "output_dp":
        "FX-DL-PACKAGE-PATH":
        "FX-DL-JSON-PATH":
        "PERFHERDER-REVISION":
        "PERFHERDER-PKG-PLATFORM":
    }

    """

    # get queue msg, consumer config from kwargs
    queue_msg, consumer_config, task_config = init_task(kwargs)

    # init download url
    remote_url_str = ArchiveMozillaHelper.DEFAULT_ARCHIVE_URL + ArchiveMozillaHelper.DEFAULT_NIGHTLY_ARCHIVE_URL_DIR + ArchiveMozillaHelper.DEFAULT_NIGHTLY_LATEST_URL_DIR

    # get output dir path from kwargs
    cmd_parameter_list = parse_cmd_parameters(queue_msg)
    if len(cmd_parameter_list) == 2:
        output_dp = cmd_parameter_list[1]
    else:
        output_dp = task_config.get("DOWNLOAD_PKG_OUTPUT_DP", os.getcwd())

    return download_nightly_build(output_dp, remote_url_str)


def link_fx_pkg():
    if sys.platform == "linux2":
        firefox_fp = FIREFOX_BIN_LINUX_FP
    elif sys.platform == "win32":
        firefox_fp = FIREFOX_BIN_WIN_FP
    else:
        firefox_fp = FIREFOX_BIN_MAC_FP
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
        os.symlink(src_link, FIREFOX_BIN_LINUX_FP)
    elif sys.platform == "darwin":
        DEFAULT_NIGHLTY_ATTACTED_PATH = "/Volumes/Nightly"
        if os.path.exists(DEFAULT_NIGHLTY_ATTACTED_PATH):
            shutil.copytree(os.path.join(DEFAULT_NIGHLTY_ATTACTED_PATH, "FirefoxNightly.app"), FIREFOX_BIN_MAC_FP)
            detach_cmd_format = "hdiutil detach %s"
            detach_cmd_str = detach_cmd_format % DEFAULT_NIGHLTY_ATTACTED_PATH
            if os.system(detach_cmd_str) != 0:
                logging.error("detach dmg file[%s] failed! cmd string: [%s]" % (DEFAULT_NIGHLTY_ATTACTED_PATH, detach_cmd_str))
        else:
            logging.error("can't find the nightly attached path [%s]" % DEFAULT_NIGHLTY_ATTACTED_PATH)
    else:
        src_path = os.path.join(os.getcwd(), "firefox")
        os.rename(src_path, FIREFOX_BIN_WIN_FP)


def extract_fx_pkg(input_fx_pkg_fp, input_fx_extract_dir="firefox"):
    if os.path.exists(input_fx_extract_dir):
        shutil.rmtree(input_fx_extract_dir)
    if input_fx_pkg_fp.endswith(".tar.bz2"):
        target_file = tarfile.open(input_fx_pkg_fp, "r:bz2")
        target_file.extractall()
        target_file.close()
    elif input_fx_pkg_fp.endswith(".zip"):
        target_file = zipfile.ZipFile(input_fx_pkg_fp, "r")
        target_file.extractall()
        target_file.close()
    else:
        attach_cmd_format = "hdiutil attach -noautoopen -quiet %s"
        attach_cmd_str = attach_cmd_format % input_fx_pkg_fp
        if os.system(attach_cmd_str) != 0:
            logging.error("attach dmg file[%s] failed! cmd string: [%s]" % (input_fx_pkg_fp, attach_cmd_str))
            return False
        else:
            logging.info("attach dmg file[%s] sucessfully!" % input_fx_pkg_fp)
    return True


def deploy_fx_package(**kwargs):
    """
    deploy firefox package to system default path
    @param kwargs:

        kwargs['cmd_obj']['configs']['INPUT_FX_DL_PKG_PATH'] :: the firefox package path your want to deploy to system default path

    @return:
    """

    # get queue msg, consumer config from kwargs
    queue_msg, consumer_config, task_config = init_task(kwargs)

    # get fx pkg path
    cmd_parameter_list = parse_cmd_parameters(queue_msg)
    if len(cmd_parameter_list) == 2:
        fx_dl_pkg_path = cmd_parameter_list[1]
    else:
        fx_dl_pkg_path = task_config.get("INPUT_FX_DL_PKG_PATH", None)

    if fx_dl_pkg_path:
        if extract_fx_pkg(fx_dl_pkg_path):
            link_fx_pkg()
            return True
        else:
            logging.error("cannot extract firefox package [%s]" % fx_dl_pkg_path)
    else:
        logging.warn("please specify firefox downloaded package path after cmd")
    return False
