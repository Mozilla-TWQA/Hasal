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

DEFAULT_UPLOAD_VIDEO_YAML_SETTING = "./mozhasalvideo.yaml"
DEFAULT_UPLOAD_VIDEO_MYCRED_TXT = "./mycreds_mozhasalvideo.txt"
DEFAULT_UPLOAD_FOLDER_URI = "0B9g1GJPq5xo8Ry1jV0s3Y3F6ZFE"
DEFAULT_CONVERT_VIDEO_RESOLUTION = "320x240"


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

    def generate_url_str(self, input_test_name, api_root=None):
        url_format = "http://%s:%s/%s"
        if api_root is None:
            api_root = self.svr_config["project_name"]
        path_str = "/".join([api_root, sys.platform, self.test_target, input_test_name])
        return url_format % (self.svr_config['svr_addr'], self.svr_config['svr_port'], path_str)

    def upload_result(self, input_result_fp):
        with open(input_result_fp) as json_fh:
            result_data = json.load(json_fh)
        if len(result_data.keys()) != 1:
            print "[ERROR] current result file consist over 1 test case result!"
            return None
        else:
            # init test data
            test_name = result_data.keys()[0]
            test_browser_type = test_name.split("_")[1]
            test_time_list = result_data[test_name]['time_list']
            test_video_fp = result_data[test_name]['video_fp']
            web_app_name = result_data[test_name]['web_app_name']
            if len(test_time_list) != 1:
                print "[ERROR] current time list is not equal to 1, current: %d!" % len(test_time_list)
                return None
            else:
                test_value = test_time_list[0]
            url_str = self.generate_url_str(test_name)

            # compose post data
            json_data = {"os": sys.platform,
                         "target": self.test_target,
                         "test": test_name,
                         "browser": test_browser_type,
                         "version": self.current_browser_version[test_browser_type],
                         "platform": platform.machine(),
                         "webappname": web_app_name,
                         "value": test_value,
                         "video": test_video_fp,
                         "comment": self.test_comment_str}

            # print post data
            print self.current_browser_version
            print "===== Upload result post data ====="
            print json_data
            print "===== Upload result post data ====="
            return json.loads(self.send_post_data(json_data, url_str).read())

    def send_post_data(self, post_data, url_str):
        query_args = {}
        # compose query and send request
        json_data_str = json.dumps(post_data)
        query_args['json'] = json_data_str
        encoded_args = urllib.urlencode(query_args)
        response_obj = urllib2.urlopen(url_str, encoded_args)
        if response_obj.getcode() == 200:
            return response_obj
        else:
            print "[ERROR] response status code is [%d]" % response_obj.getcode()
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
                url_str = self.generate_url_str(upload_data['test_name'], api_root="video_profile")
                print "===== Upload video post data ====="
                print url_str
                print json_data
                print "===== Upload video post data ====="
                self.send_post_data(json_data, url_str)
