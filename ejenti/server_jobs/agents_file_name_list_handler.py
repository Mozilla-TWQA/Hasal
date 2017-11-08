import os
import json
import logging
from lib.common.b2Util import B2Util
from lib.common.statusFileCreator import StatusFileCreator


class AgentsFileNameListHandler(object):

    KEY_FILE_NAME_LIST = 'file_name_list'
    KEY_AGENT_NAME_LIST = 'agent_name_list'
    FILE_NAME_LIST_FILE_NAME = 'file_name_list.json'

    @staticmethod
    def _get_file_name_list_from_object_list(file_object_list):
        """
        Return the file name list.
        Ref:
        @param file_object_list:
        @return:
        """
        return [obj.get('fileName') for obj in file_object_list]

    @staticmethod
    def _get_agent_name_list_from_file_name_list(file_name_list):
        """
        Return the agent name list from file name list.
        Ref:
        @param file_name_list:
        @return:
        """
        keyword_for_recently_filename = '_recently.json'
        return [name.replace(keyword_for_recently_filename, '') for name in file_name_list if name.endswith(keyword_for_recently_filename)]

    def run(self, b2_account_id, b2_account_key, b2_upload_bucket_name):
        logging.info('Agents File Name List Handler starting ...')

        agent_file_name_list_file_path = os.path.join(StatusFileCreator.get_status_folder(), AgentsFileNameListHandler.FILE_NAME_LIST_FILE_NAME)

        b2_obj = B2Util(b2_account_id, b2_account_key)
        bucket_id = b2_obj.get_bucket_id_by_name(b2_upload_bucket_name)

        logging.debug('Bucket [{}] ID is {}'.format(b2_upload_bucket_name, bucket_id))

        ret_list = b2_obj.get_file_name_list(bucket_id)

        filename_list = AgentsFileNameListHandler._get_file_name_list_from_object_list(ret_list)
        agentname_list = AgentsFileNameListHandler._get_agent_name_list_from_file_name_list(filename_list)

        ret_obj = {
            AgentsFileNameListHandler.KEY_FILE_NAME_LIST: filename_list,
            AgentsFileNameListHandler.KEY_AGENT_NAME_LIST: agentname_list
        }
        logging.debug('Get the file name list from Bucket [{}]: {}'.format(b2_upload_bucket_name, ret_obj))

        # dump to file
        with open(agent_file_name_list_file_path, "wb") as f:
            json.dump(ret_obj, f, indent=4)

        uploaded_agent_file_name_list_file_url = b2_obj.upload_file(agent_file_name_list_file_path, b2_upload_bucket_name)
        logging.info('Upload Agents File Name List to {}'.format(uploaded_agent_file_name_list_file_url))
        logging.info('Agents File Name List Handler done.')


if __name__ == '__main__':
    app = AgentsFileNameListHandler()
    app.run()
