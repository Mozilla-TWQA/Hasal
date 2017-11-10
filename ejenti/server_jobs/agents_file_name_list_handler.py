import os
import json
import logging
import datetime
from lib.common.gistUtil import GISTUtil
from lib.common.statusFileCreator import StatusFileCreator
from lib.common.commonUtil import UTC


class AgentsFileNameListHandler(object):

    KEY_FILE_NAME_LIST = 'file_name_list'
    KEY_AGENT_NAME_LIST = 'agent_name_list'
    FILE_NAME_LIST_FILE_NAME = 'file_name_list.json'

    @staticmethod
    def _strptime_to_timestamp(input_time_str):
        if input_time_str:
            # Parse UTC string into naive datetime, then add timezone
            dt = datetime.datetime.strptime(input_time_str, '%Y-%m-%dT%H:%M:%SZ')
            return int((dt.replace(tzinfo=UTC()) - datetime.datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=UTC())).total_seconds())
        return None

    @staticmethod
    def _strip_revision_for_raw_url(input_raw_url):
        return "/".join(input_raw_url.split("/")[:-2]) + "/" + input_raw_url.split("/")[-1]

    @staticmethod
    def _convert_gist_file_table_to_agent_list(input_gist_file_table_dict):
        """
        Return the agent name list from file name list.
        Ref:
        @param file_name_list:
        @return:
        """
        return_dict = {}
        keyword_for_recently_filename = '_recently.json'
        keyword_for_history_filename = '_history.json'
        for file_name in input_gist_file_table_dict:
            if file_name.find(keyword_for_recently_filename) >= 0:
                agent_host_name = file_name.split(keyword_for_recently_filename)[0]
                period_type = "recently"
            elif file_name.find(keyword_for_history_filename) >= 0:
                agent_host_name = file_name.split(keyword_for_history_filename)[0]
                period_type = "history"
            else:
                agent_host_name = None
                period_type = None
                logging.warning("Current gist user account contain file [%s] violate the naming rules!" % file_name)

            if agent_host_name:
                if agent_host_name in return_dict:
                    if period_type in return_dict[agent_host_name]:
                        logging.error("There could be duplicate period_type [%s] in generated agent list table [%s]" % (period_type, return_dict[agent_host_name]))
                    else:
                        return_dict[agent_host_name][period_type] = {
                            "file_name": file_name,
                            "url": input_gist_file_table_dict[file_name]["url"],
                            "raw_url": AgentsFileNameListHandler._strip_revision_for_raw_url(input_gist_file_table_dict[file_name]["raw_url"]),
                            "id": input_gist_file_table_dict[file_name]["id"],
                            "created_at": AgentsFileNameListHandler._strptime_to_timestamp(input_gist_file_table_dict[file_name]["created_at"]),
                            "updated_at": AgentsFileNameListHandler._strptime_to_timestamp(input_gist_file_table_dict[file_name]["updated_at"])
                        }
                else:
                    return_dict[agent_host_name] = {period_type: {
                        "file_name": file_name,
                        "url": input_gist_file_table_dict[file_name]["url"],
                        "raw_url": AgentsFileNameListHandler._strip_revision_for_raw_url(input_gist_file_table_dict[file_name]["raw_url"]),
                        "id": input_gist_file_table_dict[file_name]["id"],
                        "created_at": AgentsFileNameListHandler._strptime_to_timestamp(input_gist_file_table_dict[file_name]["created_at"]),
                        "updated_at": AgentsFileNameListHandler._strptime_to_timestamp(input_gist_file_table_dict[file_name]["updated_at"])
                    }}

        return return_dict

    def run(self, gist_user_name, gist_auth_token):
        logging.info('Agents File Name List Handler starting ...')

        agent_file_name_list_file_path = os.path.join(StatusFileCreator.get_status_folder(), AgentsFileNameListHandler.FILE_NAME_LIST_FILE_NAME)

        gist_obj = GISTUtil(gist_user_name, gist_auth_token)

        list_gists_response_obj = gist_obj.list_gists()

        if list_gists_response_obj:
            gist_file_table_dict = gist_obj.generate_gist_file_table(list_gists_response_obj.json())
        else:
            logging.error("Cannot get gist list of user [%s], skip generate agent list file!" % gist_user_name)
            return None

        agents_data = AgentsFileNameListHandler._convert_gist_file_table_to_agent_list(gist_file_table_dict)

        logging.debug('Get the file name list from GIST user [{}]: {}'.format(gist_user_name, agents_data))

        # dump to file
        with open(agent_file_name_list_file_path, "wb") as f:
            json.dump(agents_data, f, indent=4)

        uploaded_agent_file_name_list_file_url = gist_obj.upload_file(agent_file_name_list_file_path)
        logging.info('Upload Agents File Name List to {}'.format(uploaded_agent_file_name_list_file_url))
        logging.info('Agents File Name List Handler done.')
