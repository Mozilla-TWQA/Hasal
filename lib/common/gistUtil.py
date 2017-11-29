import os
import json
from commonUtil import NetworkUtil
from logConfig import get_logger

logger = get_logger(__name__)


class GISTUtil(object):

    DEFAULT_GITHUB_API_URL = 'https://api.github.com'
    DEFAULT_CTNT_TYPE_JSON = "application/json"
    DEFAULT_GIST_MAX_LIMIT_COMMITS = 1000

    def __init__(self, userName, authToken):

        self.user_name = userName
        self.auth_token = authToken

    def query_user(self):
        query_url = "%s/users/%s" % (GISTUtil.DEFAULT_GITHUB_API_URL, self.user_name)

        headers = {
            'Authorization': "token %s" % self.auth_token,
            "User-Agent": "Hasal-%s-App" % self.user_name
        }

        logger.debug("Query gist user with url:[%s], headers:[%s]" % (query_url, headers))

        return NetworkUtil.get_request_and_response(query_url, input_headers=headers, input_accept_status_code=[200, 201])

    def create_new_gist(self, input_file_name, input_file_content, input_file_desc="", input_content_type=DEFAULT_CTNT_TYPE_JSON, input_public_flag=True):
        """
        create new gist
        @param input_file_path: json file path
        @param input_file_desc:
        @param input_content_type: default is "application/json"
        @param input_public_flag: default is True
        @return: response_data
        """

        upload_url = "%s/gists" % (self.DEFAULT_GITHUB_API_URL)

        headers = {
            'Authorization': "token %s" % self.auth_token,
            'Content-Type': input_content_type,
            "User-Agent": "Hasal-%s-App" % self.user_name
        }

        post_data = """{
            "description": "%s",
            "public": %s,
            "files":
                {
                    "%s": {"content": "%s"}
                 }
        }""" % (input_file_desc, str(input_public_flag).lower(), input_file_name, input_file_content)

        logger.debug("Upload file to gist with url:[%s], headers:[%s], data:[%s]" % (upload_url, headers, post_data))

        return NetworkUtil.post_request_and_response(upload_url, post_data, headers, [200, 201])

    def update_existing_gist(self, input_gist_id, input_file_name, input_file_content, input_file_desc="", input_content_type=DEFAULT_CTNT_TYPE_JSON):
        """
        Update existing gist
        @param input_file_path:
        @param input_file_desc:
        @return:
        """

        update_url = "%s/gists/%s" % (self.DEFAULT_GITHUB_API_URL, input_gist_id)

        headers = {
            'Authorization': "token %s" % self.auth_token,
            'Content-Type': input_content_type,
            "User-Agent": "Hasal-%s-App" % self.user_name
        }

        post_data = """{
            "description": "%s",
            "files":
                {
                    "%s": {"content": "%s"}
                 }
        }""" % (input_file_desc, input_file_name, input_file_content)

        logger.debug("Upload file to gist with url:[%s], headers:[%s], data:[%s]" % (update_url, headers, post_data))

        return NetworkUtil.post_request_and_response(update_url, post_data, headers, [200, 201])

    def delete_gist(self, input_gist_id):
        delete_url = "%s/gists/%s" % (self.DEFAULT_GITHUB_API_URL, input_gist_id)

        headers = {
            'Authorization': "token %s" % self.auth_token,
            "User-Agent": "Hasal-%s-App" % self.user_name
        }

        logger.debug("delete file on gist with url:[%s], headers:[%s]" % (delete_url, headers))

        return NetworkUtil.delete_request_and_response(delete_url, input_headers=headers, input_accept_status_code=[200, 201, 204])

    def list_single_gist(self, input_gist_id, max_retry=1):
        query_url = "%s/gists/%s" % (self.DEFAULT_GITHUB_API_URL, input_gist_id)

        headers = {
            'Authorization': "token %s" % self.auth_token,
            "User-Agent": "Hasal-%s-App" % self.user_name
        }

        logger.debug("query gist with url:[%s], headers:[%s]" % (query_url, headers))

        return NetworkUtil.get_request_and_response(query_url, input_headers=headers, input_accept_status_code=[200, 201], max_retry=max_retry)

    def list_gists(self):
        headers = {
            'Authorization': "token %s" % self.auth_token,
            "User-Agent": "Hasal-%s-App" % self.user_name
        }
        query_url = "%s/users/%s/gists" % (self.DEFAULT_GITHUB_API_URL, self.user_name)
        return NetworkUtil.get_request_and_response(query_url, input_headers=headers)

    def generate_gist_file_table(self, input_gist_result_list):
        return_table_dict = {}
        for gist_obj in input_gist_result_list:
            filename_dict = gist_obj.get("files", {})
            for filename in filename_dict:
                if filename in return_table_dict:
                    logger.error("Find duplicate file name [%s] in current user [%s] gist list" % (filename, self.user_name))
                else:
                    if "history" in gist_obj:
                        revision_count = len(gist_obj["history"])
                    else:
                        revision_count = 1000
                    return_table_dict[filename] = {
                        "id": gist_obj["id"],
                        "url": gist_obj["url"],
                        "raw_url": filename_dict[filename]["raw_url"],
                        "created_at": gist_obj["created_at"],
                        "updated_at": gist_obj["updated_at"],
                        "revision_count": revision_count
                    }
        return return_table_dict

    def upload_content(self, input_file_name, input_content, input_file_desc="", input_content_type=DEFAULT_CTNT_TYPE_JSON, input_public_flag=True):
        """
        Quite simiar to upload file, will list the gists under user name before uploading, will create the gist if file
        name is not exist. If file name exists, update the existing gist
        @param input_file_name:
        @param input_content:
        @param input_file_desc:
        @param input_content_type:
        @param input_public_flag:
        @return:
        """

        # get gist list and generate gist file table
        list_gists_response_obj = self.list_gists()
        if list_gists_response_obj:
            gist_file_table_dict = self.generate_gist_file_table(list_gists_response_obj.json())
        else:
            logger.error(
                "Cannot get gist list of user [%s], skip upload file to avoid file name duplicate!" % self.user_name)
            return None

        # create new gist if file not exist, update gist if file exists
        if input_file_name in gist_file_table_dict:
            if gist_file_table_dict[input_file_name]["revision_count"] >= GISTUtil.DEFAULT_GIST_MAX_LIMIT_COMMITS:
                delete_response_obj = self.delete_gist(gist_file_table_dict[input_file_name]["id"])
                query_single_gist_obj = self.list_single_gist(gist_file_table_dict[input_file_name]["id"])
                if delete_response_obj and not query_single_gist_obj:
                    response_gist_obj = self.create_new_gist(input_file_name, input_content, input_file_desc,
                                                             input_content_type,
                                                             input_public_flag)
                else:
                    response_gist_obj = self.update_existing_gist(gist_file_table_dict[input_file_name]["id"],
                                                                  input_file_name, input_content, input_file_desc,
                                                                  input_content_type)
            else:
                response_gist_obj = self.update_existing_gist(gist_file_table_dict[input_file_name]["id"],
                                                              input_file_name, input_content, input_file_desc,
                                                              input_content_type)
        else:
            response_gist_obj = self.create_new_gist(input_file_name, input_content, input_file_desc, input_content_type,
                                                     input_public_flag)

        # get raw url of upload file
        if response_gist_obj:
            tmp_file_list = response_gist_obj.json().get("files", {}).values()
            if len(tmp_file_list) == 1:
                file_download_url = tmp_file_list[0].get("raw_url", None)
            else:
                logger.error("Gist upload failed, return obj format incorrect [%s]" % response_gist_obj.json())
                return None
            return file_download_url
        else:
            return None

    def upload_file(self, input_file_path, input_file_desc="", input_content_type=DEFAULT_CTNT_TYPE_JSON, input_public_flag=True):
        """
        This function will list the gists under user name and parsing the data to generate file name as uniqure key.
        Based on the table generate above, if file name is not exist, we will create a new gist. if not, we will update the existing gist

        @param input_file_path: json file path
        @param input_file_desc:
        @param input_content_type: default is "application/json"
        @param input_public_flag: default is True
        @return: raw data url
        """
        # init varirable
        input_file_name = os.path.basename(input_file_path)

        # get gist list and generate gist file table
        list_gists_response_obj = self.list_gists()
        if list_gists_response_obj:
            gist_file_table_dict = self.generate_gist_file_table(list_gists_response_obj.json())
        else:
            logger.error("Cannot get gist list of user [%s], skip upload file to avoid file name duplicate!" % self.user_name)
            return None

        # get file content
        if os.path.exists(input_file_path):
            with open(input_file_path, 'rb') as fh:
                if input_content_type == self.DEFAULT_CTNT_TYPE_JSON:
                    file_data = json.dumps(json.load(fh)).replace('\\', '\\\\').replace('"', '\\"')
                else:
                    file_data = fh.read()
        else:
            logger.error("The file[%s] you specify for uploading is not exist!" % input_file_path)
            return None

        # create new gist if file not exist, update gist if file exists
        if input_file_name in gist_file_table_dict:
            response_gist_obj = self.update_existing_gist(gist_file_table_dict[input_file_name]["id"], input_file_name, file_data, input_file_desc, input_content_type)
        else:
            response_gist_obj = self.create_new_gist(input_file_name, file_data, input_file_desc, input_content_type, input_public_flag)

        # get raw url of upload file
        if response_gist_obj:
            tmp_file_list = response_gist_obj.json().get("files", {}).values()
            if len(tmp_file_list) == 1:
                file_download_url = tmp_file_list[0].get("raw_url", None)
            else:
                logger.error("Gist upload failed, return obj format incorrect [%s]" % response_gist_obj.json())
                return None
            return file_download_url
        else:
            return None
