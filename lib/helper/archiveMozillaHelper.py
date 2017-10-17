import datetime
import pandas as pd
from ..common.logConfig import get_logger
from lib.common.commonUtil import NetworkUtil


logger = get_logger(__name__)


class ArchiveMozillaHelper(object):
    DEFAULT_ARCHIVE_URL = "https://archive.mozilla.org"
    DEFAULT_NIGHTLY_ARCHIVE_URL_DIR = "/pub/firefox/nightly"
    DEFAULT_NIGHTLY_LATEST_URL_DIR = "/latest-mozilla-central/"

    @staticmethod
    def get_folder_name_list(query_dir_url):
        """
        query archive mozilla folder list
        @param input_query_year:
        @param input_query_month:
        @return: folder name list ex: ['2017-09-19-22-02-02-mozilla-central-l10n/', '2017-09-19-22-02-02-mozilla-central/', ..]
        """
        response_obj = NetworkUtil.get_request_and_response(query_dir_url)
        if response_obj:
            resposne_text = response_obj.text
            response_df = pd.read_html(resposne_text, header=0, index_col=0)[0]
            response_table_dict = response_df.set_index("Name").T.to_dict()
            folder_name_list = [d_name for d_name in response_table_dict.keys() if d_name != ".."]
            folder_name_list.sort()
            return folder_name_list
        else:
            return []

    @staticmethod
    def filter_backfill_period_data(input_backfill_start_date, input_current_date, input_backfill_repo, input_folder_list, input_query_channel_archive_url):
        """

        @param input_backfill_start_date:
        @param input_current_date:
        @param input_backfill_repo:
        @param input_folder_list:
        @param input_query_channel_archive_url:
        @return: {"complete_dir_url": {"folder_name": folder_name, "folder_datetime", folder_datetime}
        ex: {"https://archive.mozilla.org/pub/firefox/nightly/2017/09/2017-09-01-10-03-09-mozilla-central/": {"folder_name": "2017-09-01-10-03-09-mozilla-central", "folder_datetime": "2017-09-01-10-03-09"}
        """
        result_dict = {}
        for folder_name in input_folder_list:
            folder_datetime = datetime.datetime.strptime("-".join(folder_name.split("-")[:6]), '%Y-%m-%d-%H-%M-%S')
            channel_name = "-".join(folder_name.split("-")[6:])
            if channel_name == input_backfill_repo:
                if input_backfill_start_date <= folder_datetime <= input_current_date:
                    complete_dir_url = "%s/%s/%s" % (input_query_channel_archive_url, folder_datetime.strftime("%Y/%m"), folder_name)
                    if complete_dir_url not in result_dict:
                        result_dict[complete_dir_url] = {"folder_name": folder_name,
                                                         "folder_datetime": "-".join(folder_name.split("-")[:6])}
                    else:
                        logger.warning("Duplicate folder url exist!!! [%s]" % complete_dir_url)
        return result_dict

    @staticmethod
    def get_backfill_folder_dict(input_backfill_days, input_backfill_repo, input_app_name, input_channel_name, input_history_folder_list):
        """
        base on backfill day and channel filter the archive folder list
        @param input_backfill_days:
        @param input_backfill_repo:
        @param input_app_name: check the example: https://archive.mozilla.org/pub/<input_app_name>/<input_channel_name>
        @param input_channel_name: check the example: https://archive.mozilla.org/pub/<input_app_name>/<input_channel_name>
        @param input_history_folder_list:
        @return:
         {
           "https://archive.mozilla.org/pub/firefox/nightly/2017/09/2017-09-15-10-01-21-mozilla-central/": {"folder_name": "2017-09-15-10-01-21-mozilla-central/",
                                                                                                            "folder_datetime": "2017-09-15-10-01-21"}
         }
        """

        current_utc_time = datetime.datetime.utcnow()
        shift_days = datetime.timedelta(days=input_backfill_days)
        backfill_start_date = current_utc_time - shift_days
        backfill_start_year = backfill_start_date.strftime("%Y")
        backfill_start_month = backfill_start_date.strftime("%m")
        backfill_start_day = backfill_start_date.strftime("%d")
        backfill_start_date_without_time = datetime.datetime.strptime(backfill_start_year + "-" + backfill_start_month + "-" + backfill_start_day, "%Y-%m-%d")
        current_year = current_utc_time.strftime("%Y")
        current_month = current_utc_time.strftime("%m")
        DEFAULT_QUERY_CHANNEL_ARCHIVE_URL = "%s/pub/%s/%s" % (ArchiveMozillaHelper.DEFAULT_ARCHIVE_URL, input_app_name, input_channel_name)
        query_dir_url = "%s/%d/%02d/" % (DEFAULT_QUERY_CHANNEL_ARCHIVE_URL, int(backfill_start_year), int(backfill_start_month))
        total_folder_list = ArchiveMozillaHelper.get_folder_name_list(query_dir_url)
        if backfill_start_year != current_year or backfill_start_month != current_month:
            query_dir_url = "%s/%d/%02d/" % (DEFAULT_QUERY_CHANNEL_ARCHIVE_URL, int(current_year), int(current_month))
            total_folder_list.extend(ArchiveMozillaHelper.get_folder_name_list(query_dir_url))
        for history_folder_name in input_history_folder_list:
            if history_folder_name not in total_folder_list:
                total_folder_list.append(history_folder_name)
        return ArchiveMozillaHelper.filter_backfill_period_data(backfill_start_date_without_time, current_utc_time, input_backfill_repo, total_folder_list, DEFAULT_QUERY_CHANNEL_ARCHIVE_URL)

    @staticmethod
    def get_fx_pkg_name(input_platform_name, input_url_str):
        """
        get corresponding platform name from remote url dir

        @param input_platform_name:
        @param input_url_str:
        @return: pkg file and json url dir path
        """
        PLATFORM_FN_MAPPING = {'linux32': {'key': 'linux-i686', 'ext': 'tar.bz2', 'trydl': 'linux', 'job': ['linux32']},
                               'linux64': {'key': 'linux-x86_64', 'ext': 'tar.bz2', 'trydl': 'linux64',
                                           'job': ['linux64']},
                               'mac': {'key': 'mac', 'ext': 'dmg', 'trydl': 'macosx64', 'job': ['osx']},
                               'win32': {'key': 'win32', 'ext': 'zip', 'trydl': 'win32', 'job': ['windows', '32']},
                               'win64': {'key': 'win64', 'ext': 'zip', 'trydl': 'win64', 'job': ['windows', '64']}}

        remote_file_dict = NetworkUtil.get_files_from_remote_url_folder(input_url_str)

        # filter with platform, and return file name with extension
        if len(remote_file_dict.keys()) == 0:
            logger.error(
                "can't get remote file list, could be the network error, or url path[%s] wrong!!" % input_url_str)
            return False
        else:
            if input_platform_name not in PLATFORM_FN_MAPPING:
                logger.error("we are currently not support the platform[%s] you specified!" % input_platform_name)
                logger.error("We are currently support the platform tag: [%s]" % PLATFORM_FN_MAPPING.keys())
                return False
            else:
                matched_keyword = PLATFORM_FN_MAPPING[input_platform_name]['key'] + "." + PLATFORM_FN_MAPPING[input_platform_name]['ext']
                matched_file_list = [fn for fn in remote_file_dict.keys()
                                     if ((matched_keyword in fn) and ('firefox' in fn) and (not fn.endswith('.asc')))]
                if len(matched_file_list) != 1:
                    logger.warn("the possible match file list is not equal 1, list as below: [%s]" % matched_file_list)
                    if len(matched_file_list) < 1:
                        return False
                    matched_file_list = sorted(matched_file_list)[-1:]
                    logger.warn("select following file [%s]" % matched_file_list)

        # combine file name with json
        matched_file_name = matched_file_list[0]
        matched_json_file_name = matched_file_name.replace(PLATFORM_FN_MAPPING[input_platform_name]['key'] + "." + PLATFORM_FN_MAPPING[input_platform_name]['ext'], PLATFORM_FN_MAPPING[input_platform_name]['key'] + ".json")
        if matched_json_file_name not in remote_file_dict:
            logger.error("can't find the json file[%s] in remote file list[%s]!" % (matched_json_file_name, remote_file_dict))
            return None, None
        else:
            logger.debug("matched file name: [%s], json_file_name: [%s]" % (matched_file_name, matched_json_file_name))

        return remote_file_dict[matched_file_name], remote_file_dict[matched_json_file_name]
