from __future__ import print_function
import re
import os
import copy
import json
from ..common.logConfig import get_logger
from lib.common.commonUtil import NetworkUtil


logger = get_logger(__name__)


class PerfherderDataQueryHelper(object):
    DEFAULT_HASAL_SIGNATURES = "hasal_perfherder_signatures.json"
    DEFAULT_PERFHERDER_PRODUCTION_URL = "https://treeherder.mozilla.org"
    DEFAULT_PERFHERDER_STAGE_URL = "https://treeherder.allizom.org"
    API_URL_QUERY_SIGNATURE_LIST = "%s/api/project/%s/performance/signatures/"
    API_URL_QUERY_DATA = "%s/api/project/%s/performance/data/"

    @staticmethod
    def query_all_signatures(input_channel_name="mozilla-central", input_framework_no=9):
        """
        query all signatures from the given framework no and channel name
        @param input_channel_name:
        @param input_framework_no: Hasal framework no default is 9
        @return:
        """
        query_url_str = PerfherderDataQueryHelper.API_URL_QUERY_SIGNATURE_LIST % (PerfherderDataQueryHelper.DEFAULT_PERFHERDER_PRODUCTION_URL)
        query_params = {"format": "json", "framework": str(input_framework_no)}
        query_header = {'User-Agent': "Hasal Query Perfherder Tool"}
        return_result = {'signature_data': {}, 'suite_list': [], 'browser_type_list': [], 'machine_platform_list': []}

        query_response = NetworkUtil.get_request_and_response(input_url=query_url_str, input_params=query_params, input_headers=query_header)
        if query_response:
            json_obj = query_response.json()
            for revision in json_obj.keys():
                if 'test' not in json_obj[revision] and 'parent_signature' not in json_obj[revision] and 'has_subtests' in json_obj[revision]:
                    suite_name = json_obj[revision]['suite'].strip()
                    browser_type = json_obj[revision]['extra_options'][0].strip()
                    machine_platform = json_obj[revision]['machine_platform'].strip()
                    return_result['signature_data'][revision] = {'suite_name': suite_name,
                                                                 'browser_type': browser_type,
                                                                 'machine_platform': machine_platform}
                    if suite_name not in return_result['suite_list']:
                        return_result['suite_list'].append(suite_name)
                    if browser_type not in return_result['browser_type_list']:
                        return_result['browser_type_list'].append(browser_type)
                    if machine_platform not in return_result['machine_platform_list']:
                        return_result['machine_platform_list'].append(machine_platform)
            with open(PerfherderDataQueryHelper.DEFAULT_HASAL_SIGNATURES, "w+") as fh:
                json.dump(return_result, fh)
        return return_result

    @staticmethod
    def filter_signatures_by_whitelist(input_signatures_data, input_white_list):
        if len(input_white_list) > 0:
            for pattern in input_white_list:
                logger.debug('Filter Black word by pattern: {}'.format(pattern))
                for sig_key, sig_obj in input_signatures_data['signature_data'].items():
                    suite_name = sig_obj.get('suite_name', '')
                    if re.match(pattern, suite_name):
                        logger.debug('Del sig [{sig}] with suite name [{suite_name}]'.format(sig=sig_key, suite_name=suite_name))
                        del input_signatures_data['signature_data'][sig_key]
        return input_signatures_data

    @staticmethod
    def convert_query_result(input_json, signature_data, input_result_dict):
        """
        generate a list which contains the result from input_json and signature_data between begin and end date.
        @param input_json:
        @param signature_data:
        @return: a list which contains result
        """
        for sig in input_json:
            for data in input_json[sig]:
                suite_name_full = signature_data['signature_data'][sig]['suite_name'].split()
                suite_name = suite_name_full[0]
                push_tiemstamp = data['push_timestamp']
                perfherder_data_index = "%s:%s:%s" % (suite_name, signature_data['signature_data'][sig]['browser_type'], signature_data['signature_data'][sig]['machine_platform'])
                if push_tiemstamp in input_result_dict:
                    if perfherder_data_index in input_result_dict[push_tiemstamp]['perfherder_data']:
                        input_result_dict[push_tiemstamp]['perfherder_data'][perfherder_data_index]['value'].append(data['value'])
                    else:
                        input_result_dict[push_tiemstamp]['perfherder_data'][perfherder_data_index] = {"value": [data['value']],
                                                                                                       "signature": sig}
                else:
                    input_result_dict[push_tiemstamp] = {'perfherder_data': {perfherder_data_index: {"value": [data['value']],
                                                                                                     "signature": sig}}}
        return input_result_dict

    @staticmethod
    def get_perfherder_data(input_white_list, input_query_days=14, input_query_channel="mozilla-central", input_hasal_framework_no=9):
        """

        @param input_white_list: regular expression list ex: ['^youtube_ail_type_in_search_field ', ]
        @param input_query_days: int, query days
        @param input_query_channel: string, ex: "mozilla-central", "mozilla-beta" etc.
        @param input_hasal_framework_no: int, hasal is always 9
        @return:
        """
        query_interval = input_query_days * 24 * 60 * 60

        if not os.path.exists(PerfherderDataQueryHelper.DEFAULT_HASAL_SIGNATURES):
            raw_signature_data = PerfherderDataQueryHelper.query_all_signatures(input_channel_name=input_query_channel, input_framework_no=input_hasal_framework_no)
        else:
            with open(PerfherderDataQueryHelper.DEFAULT_HASAL_SIGNATURES) as fh:
                raw_signature_data = json.load(fh)

        filtered_signature_data = PerfherderDataQueryHelper.filter_signatures_by_whitelist(input_signatures_data=raw_signature_data, input_white_list=input_white_list)
        filtered_signature_list = copy.deepcopy(filtered_signature_data['signature_data'].keys())

        all_result_dict = {}
        counter = 0
        for signature in filtered_signature_list:
            counter += 1
            query_header = {'User-Agent': "Hasal Query Perfherder Tool"}
            query_url_str = PerfherderDataQueryHelper.API_URL_QUERY_DATA % (PerfherderDataQueryHelper.DEFAULT_PERFHERDER_PRODUCTION_URL, input_query_channel)
            query_params = {"format": "json", "framework": str(input_hasal_framework_no), "interval": str(query_interval), "signatures": signature}

            logger.debug('Query with sig [{}] ...'.format(signature))
            query_response = NetworkUtil.get_request_and_response(input_url=query_url_str, input_params=query_params, input_headers=query_header)
            logger.debug('Query with sig [{}] done.'.format(signature))

            if query_response:
                json_obj = query_response.json()
                logger.debug('\rStarting query result ... {counter}/{total}'.format(counter=counter, total=len(filtered_signature_list)), end='')
                PerfherderDataQueryHelper.convert_query_result(json_obj, filtered_signature_data, all_result_dict)

        return all_result_dict
