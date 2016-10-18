import os
import json
import sys
import urllib
import urllib2
import platform
import desktopHelper
import videoHelper
from datetime import date
from ..common.pyDriveUtil import PyDriveUtil
from desktopHelper import DEFAULT_BROWSER_TYPE_FIREFOX
from desktopHelper import DEFAULT_BROWSER_TYPE_CHROME
from ..common.logConfig import get_logger

DEFAULT_UPLOAD_VIDEO_YAML_SETTING = "./mozhasalvideo.yaml"
DEFAULT_UPLOAD_VIDEO_MYCRED_TXT = "./mycreds_mozhasalvideo.txt"
DEFAULT_UPLOAD_FOLDER_URI = "0B9g1GJPq5xo8Ry1jV0s3Y3F6ZFE"
DEFAULT_CONVERT_VIDEO_RESOLUTION = "320x240"

logger = get_logger(__name__)


class UploadAgent(object):

    def __init__(self, **kwargs):
        for variable_name in kwargs.keys():
            setattr(self, variable_name, kwargs[variable_name])

        # load server config
        with open(self.svr_config_fp) as svr_config_fh:
            self.svr_config = json.load(svr_config_fh)

        # get default installation path's browser version
        self.current_browser_version = {
            DEFAULT_BROWSER_TYPE_FIREFOX: desktopHelper.get_browser_version(DEFAULT_BROWSER_TYPE_FIREFOX),
            DEFAULT_BROWSER_TYPE_CHROME: desktopHelper.get_browser_version(DEFAULT_BROWSER_TYPE_CHROME)}

        # init test target variable
        self.test_target = "%s_%s" % (DEFAULT_BROWSER_TYPE_FIREFOX, self.current_browser_version[DEFAULT_BROWSER_TYPE_FIREFOX])

        # convert test comment
        if self.test_comment == "<today>":
            self.test_comment_str = date.today().strftime("%Y-%m-%d")
        else:
            self.test_comment_str = self.test_comment

    def generate_url_str(self, api_root=None):
        url_format = "http://%s:%s/%s"
        if api_root is None:
            api_root = self.svr_config["project_name"]
        path_str = "/".join([api_root, sys.platform, self.test_target, self.test_comment_str])
        return url_format % (self.svr_config['svr_addr'], self.svr_config['svr_port'], path_str)

    def upload_register_data(self, input_suite_fp, test_type):
        # Sample data
        # hasal_perf_reg/os/target/comment
        # sampe output {'firefox':{'regression_gsheet':['test_firefox_gsheet_1000r_number_chars_deleteallcell']},
        #               'chrome': {'regression_gsheet':['test_chrome_gsheet_1000r_number_chars_deleteallcell']}}
        with open(input_suite_fp) as input_suite_fh:
            upload_data = {}
            for tmp_line in input_suite_fh.read().splitlines():
                case_full_path = tmp_line.split(",")[0]
                if test_type == "pt":
                    tmp_list = case_full_path.split(os.sep)
                else:
                    tmp_list = case_full_path.split(".")
                browser_type = tmp_list[3].split("_")[1].lower()
                app_name = tmp_list[2].lower()
                t_type = tmp_list[1].lower()
                c_name = tmp_list[3].lower()
                if browser_type not in upload_data:
                    upload_data[browser_type] = {}
                if app_name == "t15":
                    suite_name = "t15_summary"
                else:
                    suite_name = t_type + "_" + app_name
                if suite_name in upload_data[browser_type]:
                    upload_data[browser_type][suite_name].append(c_name)
                else:
                    upload_data[browser_type] = {suite_name: [c_name]}
            url_str = self.generate_url_str("hasal_perf_reg")
            logger.info("===== Upload register suite data =====")
            logger.debug(url_str)
            logger.info(upload_data)
            logger.info("===== Upload register suite data =====")
            self.send_post_data(upload_data, url_str)

    def upload_result(self, input_result_fp):
        with open(input_result_fp) as json_fh:
            result_data = json.load(json_fh)
        if len(result_data.keys()) != 1:
            logger.error("current result file consist over 1 test case result!")
            return None
        else:
            # init test data
            test_name = result_data.keys()[0]
            test_browser_type = test_name.split("_")[1]
            test_time_list = result_data[test_name]['time_list']
            test_video_fp = result_data[test_name]['video_fp']
            web_app_name = result_data[test_name]['web_app_name']
            revision = result_data[test_name]['revision']
            if len(test_time_list) != 1:
                logger.error("current time list is not equal to 1, current: %d!" % len(test_time_list))
                return None
            else:
                test_value = test_time_list[0]['run_time']
                si_value = test_time_list[0]['si']
                psi_value = test_time_list[0]['psi']
            url_str = self.generate_url_str()

            # compose post data
            json_data = {"os": sys.platform,
                         "target": self.test_target,
                         "test": test_name,
                         "browser": test_browser_type,
                         "version": self.current_browser_version[test_browser_type],
                         "revision": revision,
                         "platform": platform.machine(),
                         "webappname": web_app_name,
                         "value": test_value,
                         "si": si_value,
                         "psi": psi_value,
                         "video": test_video_fp,
                         "comment": self.test_comment_str}

            # print post data
            logger.debug(self.current_browser_version)
            logger.info("===== Upload result post data =====")
            logger.info(json_data)
            logger.info("===== Upload result post data =====")
            return json.loads(self.send_post_data(json_data, url_str).read())

    def send_post_data(self, post_data, url_str):
        query_args = {}
        # compose query and send request
        json_data_str = json.dumps(post_data)
        query_args['json'] = json_data_str
        encoded_args = urllib.urlencode(query_args)
        response_obj = urllib2.urlopen(url_str, encoded_args)
        if response_obj.getcode() == 200:
            logger.info('response object data : [%s]' % response_obj.read())
            return response_obj
        else:
            logger.error("response status code is [%d]" % response_obj.getcode())
            return None

    def upload_videos(self, input_upload_list):
        pyDriveObj = PyDriveUtil(settings={"settings_file": DEFAULT_UPLOAD_VIDEO_YAML_SETTING,
                                           "local_cred_file": DEFAULT_UPLOAD_VIDEO_MYCRED_TXT})
        for upload_data in input_upload_list:
            if os.path.exists(upload_data['video_path']):
                new_video_path = upload_data['video_path'].replace(".mkv", ".mp4")
                videoHelper.convert_video_to_specify_size(upload_data['video_path'], new_video_path,
                                                          DEFAULT_CONVERT_VIDEO_RESOLUTION)
                upload_result = pyDriveObj.upload_file(DEFAULT_UPLOAD_FOLDER_URI, new_video_path)
                video_preview_url = "/".join(upload_result['alternateLink'].split("/")[:-1]) + "/preview"
                test_browser_type = upload_data['test_name'].split("_")[1]
                json_data = {"os": sys.platform,
                             "target": self.test_target,
                             "test": upload_data['test_name'],
                             "browser": test_browser_type,
                             "version": self.current_browser_version[test_browser_type],
                             "video_path": video_preview_url,
                             "comment": self.test_comment_str}
                url_str = self.generate_url_str("video_profile")
                logger.info("===== Upload video post data =====")
                logger.debug(url_str)
                logger.info(json_data)
                logger.info("===== Upload video post data =====")
                self.send_post_data(json_data, url_str)
